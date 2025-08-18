"""Natural language command interpretation for SSH operations."""

import re
from typing import Dict, List, Optional, Tuple
from .models import UserIntent


class CommandInterpreter:
    """Interprets natural language commands and maps them to SSH operations."""
    
    def __init__(self):
        self.command_patterns = self._init_command_patterns()
    
    def _init_command_patterns(self) -> Dict[str, List[Dict]]:
        """Initialize command patterns for different intents."""
        return {
            'check_os_version': [
                {
                    'patterns': [
                        r'查看.*作業系統.*版本',
                        r'檢查.*系統.*版本',
                        r'看.*OS.*版本',
                        r'check.*os.*version',
                        r'show.*system.*version',
                        r'what.*operating.*system'
                    ],
                    'commands': [
                        'cat /etc/os-release',
                        'uname -a',
                        'lsb_release -a'
                    ],
                    'description': '檢查作業系統版本'
                }
            ],
            'install_cuda': [
                {
                    'patterns': [
                        r'安裝.*CUDA',
                        r'裝.*CUDA',
                        r'install.*cuda',
                        r'setup.*cuda',
                        r'配置.*CUDA'
                    ],
                    'commands': [
                        'nvidia-smi',  # First check if NVIDIA driver exists
                        'wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin',
                        'sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600',
                        'wget https://developer.download.nvidia.com/compute/cuda/12.2.0/local_installers/cuda-repo-ubuntu2004-12-2-local_12.2.0-535.54.03-1_amd64.deb',
                        'sudo dpkg -i cuda-repo-ubuntu2004-12-2-local_12.2.0-535.54.03-1_amd64.deb',
                        'sudo cp /var/cuda-repo-ubuntu2004-12-2-local/cuda-*-keyring.gpg /usr/share/keyrings/',
                        'sudo apt-get update',
                        'sudo apt-get -y install cuda'
                    ],
                    'description': '安裝 NVIDIA CUDA 工具包'
                }
            ],
            'check_devices': [
                {
                    'patterns': [
                        r'檢查.*裝置.*設備',
                        r'查看.*設備',
                        r'看.*硬體.*設備',
                        r'check.*devices',
                        r'list.*devices',
                        r'show.*hardware',
                        r'what.*devices'
                    ],
                    'commands': [
                        'lspci',  # PCI devices
                        'lsusb',  # USB devices
                        'lsblk',  # Block devices
                        'nvidia-smi',  # NVIDIA GPUs if available
                        'lscpu',  # CPU information
                        'free -h',  # Memory information
                        'df -h'   # Disk information
                    ],
                    'description': '檢查系統硬體設備'
                }
            ],
            'system_status': [
                {
                    'patterns': [
                        r'系統.*狀態',
                        r'檢查.*系統',
                        r'system.*status',
                        r'check.*system',
                        r'系統.*資訊'
                    ],
                    'commands': [
                        'uptime',
                        'free -h',
                        'df -h',
                        'ps aux --sort=-%cpu | head -10',
                        'netstat -tuln'
                    ],
                    'description': '檢查系統狀態和資源使用情況'
                }
            ],
            'network_info': [
                {
                    'patterns': [
                        r'網路.*資訊',
                        r'檢查.*網路',
                        r'network.*info',
                        r'check.*network',
                        r'IP.*位址'
                    ],
                    'commands': [
                        'ip addr show',
                        'netstat -rn',
                        'ping -c 4 8.8.8.8'
                    ],
                    'description': '檢查網路配置和連線狀態'
                }
            ]
        }
    
    def interpret_command(self, user_input: str) -> UserIntent:
        """Interpret user input and return structured intent."""
        user_input = user_input.strip().lower()
        
        best_match = None
        best_confidence = 0.0
        
        for intent, pattern_groups in self.command_patterns.items():
            for pattern_group in pattern_groups:
                for pattern in pattern_group['patterns']:
                    if re.search(pattern, user_input, re.IGNORECASE):
                        # Simple confidence scoring based on pattern match
                        confidence = len(re.findall(pattern, user_input, re.IGNORECASE)) * 0.8
                        if len(user_input.split()) <= 10:  # Bonus for concise commands
                            confidence += 0.2
                        
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = {
                                'intent': intent,
                                'commands': pattern_group['commands'],
                                'description': pattern_group['description']
                            }
        
        if best_match and best_confidence > 0.5:
            return UserIntent(
                action=best_match['intent'],
                parameters={
                    'commands': best_match['commands'],
                    'description': best_match['description']
                },
                confidence=min(best_confidence, 1.0),
                original_text=user_input
            )
        else:
            # Fallback for unrecognized commands
            return UserIntent(
                action='unknown',
                parameters={'original_text': user_input},
                confidence=0.0,
                original_text=user_input
            )
    
    def get_command_suggestions(self, partial_input: str) -> List[str]:
        """Get command suggestions based on partial input."""
        suggestions = []
        partial_input = partial_input.lower()
        
        for intent, pattern_groups in self.command_patterns.items():
            for pattern_group in pattern_groups:
                description = pattern_group['description']
                # Simple matching based on keywords
                if any(keyword in partial_input for keyword in ['查看', '檢查', '安裝', 'check', 'install', 'show']):
                    suggestions.append(description)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def add_custom_pattern(self, intent: str, patterns: List[str], commands: List[str], description: str):
        """Add custom command pattern."""
        if intent not in self.command_patterns:
            self.command_patterns[intent] = []
        
        self.command_patterns[intent].append({
            'patterns': patterns,
            'commands': commands,
            'description': description
        })
    
    def get_available_intents(self) -> Dict[str, str]:
        """Get all available intents and their descriptions."""
        intents = {}
        for intent, pattern_groups in self.command_patterns.items():
            if pattern_groups:
                intents[intent] = pattern_groups[0]['description']
        return intents