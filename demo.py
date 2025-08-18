#!/usr/bin/env python3
"""Demo script for SSH AI Assistant."""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ai_agent import AIAgent
from src.models import MachineConfig
from rich.console import Console
from rich.panel import Panel

console = Console()


def demo_command_interpretation():
    """Demonstrate command interpretation capabilities."""
    console.print(Panel.fit(
        "[bold blue]SSH AI Assistant - Command Interpretation Demo[/bold blue]",
        title="演示"
    ))
    
    agent = AIAgent()
    
    # Test commands
    test_commands = [
        "幫我查看這台作業系統版本",
        "幫我安裝CUDA", 
        "幫我檢查當前裝置有哪些設備",
        "檢查系統狀態",
        "查看網路資訊",
        "check os version",
        "install cuda",
        "list devices"
    ]
    
    console.print("\n[bold]指令解析測試:[/bold]")
    
    for command in test_commands:
        intent = agent.command_interpreter.interpret_command(command)
        
        console.print(f"\n[cyan]輸入:[/cyan] {command}")
        console.print(f"[green]動作:[/green] {intent.action}")
        console.print(f"[yellow]信心度:[/yellow] {intent.confidence:.2f}")
        
        if intent.action != "unknown":
            description = intent.parameters.get('description', 'N/A')
            console.print(f"[blue]描述:[/blue] {description}")
            
            commands = intent.parameters.get('commands', [])
            if commands:
                console.print(f"[magenta]將執行的指令:[/magenta]")
                for i, cmd in enumerate(commands[:3], 1):  # Show first 3 commands
                    console.print(f"  {i}. {cmd}")
                if len(commands) > 3:
                    console.print(f"  ... 還有 {len(commands) - 3} 個指令")


def demo_machine_management():
    """Demonstrate machine management capabilities."""
    console.print(Panel.fit(
        "[bold blue]Machine Management Demo[/bold blue]",
        title="機器管理演示"
    ))
    
    agent = AIAgent()
    
    # Add demo machines
    demo_machines = [
        {
            "id": "web-server-01",
            "name": "Web Server 01",
            "host": "192.168.1.100",
            "username": "webadmin",
            "password": "demo_password",
            "description": "Production web server"
        },
        {
            "id": "db-server-01", 
            "name": "Database Server 01",
            "host": "192.168.1.101",
            "username": "dbadmin",
            "password": "demo_password",
            "description": "Production database server"
        }
    ]
    
    console.print("\n[bold]添加演示機器:[/bold]")
    
    for machine_config in demo_machines:
        # Note: In demo mode, we skip connection testing
        machine = MachineConfig(**machine_config)
        success = agent.machine_manager.add_machine(machine)
        
        if success:
            console.print(f"[green]✓[/green] 已添加: {machine.name} ({machine.host})")
        else:
            console.print(f"[red]✗[/red] 添加失敗: {machine.name}")
    
    # List machines
    console.print("\n[bold]機器列表:[/bold]")
    machines = agent.list_machines()
    
    for machine in machines:
        console.print(f"[cyan]ID:[/cyan] {machine['id']}")
        console.print(f"[green]名稱:[/green] {machine['name']}")
        console.print(f"[blue]主機:[/blue] {machine['host']}:{machine['port']}")
        console.print(f"[yellow]描述:[/yellow] {machine.get('description', 'N/A')}")
        console.print()


def demo_conversation_flow():
    """Demonstrate conversation flow."""
    console.print(Panel.fit(
        "[bold blue]Conversation Flow Demo[/bold blue]",
        title="對話流程演示"
    ))
    
    agent = AIAgent()
    
    # Create session
    session_id = agent.create_session()
    console.print(f"[green]✓[/green] 創建會話: {session_id[:8]}...")
    
    # Add a demo machine (without connection testing)
    demo_machine = MachineConfig(
        id="demo-machine",
        name="Demo Machine",
        host="demo.example.com",
        username="demo",
        password="demo"
    )
    agent.machine_manager.add_machine(demo_machine)
    
    console.print("\n[bold]模擬對話流程:[/bold]")
    
    # Simulate conversation steps
    steps = [
        ("查看可用機器", "machines"),
        ("選擇機器", f"select demo-machine"),
        ("查詢系統版本", "幫我查看這台作業系統版本"),
        ("檢查設備", "幫我檢查當前裝置有哪些設備")
    ]
    
    for step_name, command in steps:
        console.print(f"\n[cyan]步驟:[/cyan] {step_name}")
        console.print(f"[yellow]指令:[/yellow] {command}")
        
        if command == "machines":
            machines = agent.list_machines()
            console.print(f"[green]結果:[/green] 找到 {len(machines)} 台機器")
        
        elif command.startswith("select"):
            # Note: This would fail in real scenario without SSH connection
            console.print("[green]結果:[/green] 機器選擇 (演示模式)")
        
        else:
            # Demonstrate command interpretation
            intent = agent.command_interpreter.interpret_command(command)
            console.print(f"[green]結果:[/green] 解析為 '{intent.action}' (信心度: {intent.confidence:.2f})")


def main():
    """Run all demos."""
    console.print(Panel.fit(
        "[bold green]SSH AI Assistant Demo[/bold green]\n"
        "這個演示展示了系統的主要功能，包括:\n"
        "• 自然語言指令解析\n"
        "• 機器配置管理\n" 
        "• 對話流程模擬",
        title="歡迎"
    ))
    
    try:
        demo_command_interpretation()
        console.print("\n" + "="*60 + "\n")
        
        demo_machine_management()
        console.print("\n" + "="*60 + "\n")
        
        demo_conversation_flow()
        
        console.print(Panel.fit(
            "[bold green]演示完成！[/bold green]\n"
            "要開始使用系統，請執行:\n"
            "[cyan]python main.py interactive[/cyan]",
            title="完成"
        ))
        
    except Exception as e:
        console.print(f"[red]演示過程中發生錯誤: {e}[/red]")


if __name__ == "__main__":
    main()