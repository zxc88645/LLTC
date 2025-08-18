"""Command-line interface for the SSH AI system."""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.text import Text
import uuid
from typing import Dict, Any

from .ai_agent import AIAgent
from .models import MachineConfig


console = Console()


class CLIInterface:
    """Command-line interface for interacting with the SSH AI system."""
    
    def __init__(self):
        self.agent = AIAgent()
        self.current_session = None
    
    def start_interactive_mode(self):
        """Start interactive conversation mode."""
        console.print(Panel.fit(
            "[bold blue]SSH AI Assistant[/bold blue]\n"
            "自然語言 SSH 指令執行助手\n\n"
            "輸入 'help' 查看可用指令\n"
            "輸入 'quit' 或 'exit' 退出",
            title="歡迎使用"
        ))
        
        # Create new session
        self.current_session = self.agent.create_session()
        
        while True:
            try:
                user_input = Prompt.ask("\n[bold green]您[/bold green]")
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    console.print("[yellow]再見！[/yellow]")
                    break
                
                elif user_input.lower() in ['help', '幫助']:
                    self._show_help()
                
                elif user_input.lower().startswith('select'):
                    self._handle_machine_selection(user_input)
                
                elif user_input.lower() in ['machines', '機器列表']:
                    self._show_machines()
                
                elif user_input.lower().startswith('add machine'):
                    self._add_machine_interactive()
                
                else:
                    self._process_command(user_input)
            
            except KeyboardInterrupt:
                console.print("\n[yellow]再見！[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]錯誤: {e}[/red]")
    
    def _show_help(self):
        """Show help information."""
        help_text = """
[bold]可用指令:[/bold]

[cyan]機器管理:[/cyan]
• machines - 顯示所有機器
• select <machine_id> - 選擇機器
• add machine - 添加新機器

[cyan]自然語言指令範例:[/cyan]
• 幫我查看這台作業系統版本
• 幫我安裝CUDA
• 幫我檢查當前裝置有哪些設備
• 檢查系統狀態
• 查看網路資訊

[cyan]其他:[/cyan]
• help - 顯示此幫助
• quit/exit - 退出程式
        """
        console.print(Panel(help_text, title="幫助"))
    
    def _show_machines(self):
        """Display all available machines."""
        machines = self.agent.list_machines()
        
        if not machines:
            console.print("[yellow]沒有配置的機器。使用 'add machine' 添加新機器。[/yellow]")
            return
        
        table = Table(title="可用機器")
        table.add_column("ID", style="cyan")
        table.add_column("名稱", style="green")
        table.add_column("主機", style="blue")
        table.add_column("端口", style="magenta")
        table.add_column("描述", style="white")
        
        for machine in machines:
            table.add_row(
                machine["id"][:8] + "...",
                machine["name"],
                machine["host"],
                str(machine["port"]),
                machine.get("description", "")
            )
        
        console.print(table)
    
    def _handle_machine_selection(self, user_input: str):
        """Handle machine selection command."""
        parts = user_input.split()
        if len(parts) < 2:
            console.print("[red]請指定機器 ID: select <machine_id>[/red]")
            return
        
        machine_id = parts[1]
        result = self.agent.select_machine(self.current_session, machine_id)
        
        if result["success"]:
            machine = result["machine"]
            console.print(f"[green]已選擇機器: {machine['name']} ({machine['host']})[/green]")
        else:
            console.print(f"[red]選擇機器失敗: {result['error']}[/red]")
    
    def _add_machine_interactive(self):
        """Interactive machine addition."""
        console.print("[bold]添加新機器[/bold]")
        
        try:
            machine_id = str(uuid.uuid4())
            name = Prompt.ask("機器名稱")
            host = Prompt.ask("主機 IP 或域名")
            port = int(Prompt.ask("SSH 端口", default="22"))
            username = Prompt.ask("用戶名")
            
            # Choose authentication method
            auth_method = Prompt.ask(
                "認證方式",
                choices=["password", "key"],
                default="password"
            )
            
            password = None
            private_key_path = None
            
            if auth_method == "password":
                password = Prompt.ask("密碼", password=True)
            else:
                private_key_path = Prompt.ask("私鑰文件路徑")
            
            description = Prompt.ask("描述 (可選)", default="")
            
            machine_config = {
                "id": machine_id,
                "name": name,
                "host": host,
                "port": port,
                "username": username,
                "password": password,
                "private_key_path": private_key_path,
                "description": description
            }
            
            result = self.agent.add_machine(machine_config)
            
            if result["success"]:
                console.print(f"[green]機器添加成功！ID: {result['machine_id'][:8]}...[/green]")
            else:
                console.print(f"[red]添加機器失敗: {result['error']}[/red]")
        
        except Exception as e:
            console.print(f"[red]添加機器時發生錯誤: {e}[/red]")
    
    def _process_command(self, user_input: str):
        """Process natural language command."""
        if not self.current_session:
            console.print("[red]會話無效，請重新啟動[/red]")
            return
        
        context = self.agent.get_session(self.current_session)
        if not context.selected_machine:
            console.print("[yellow]請先選擇一台機器。使用 'machines' 查看可用機器，然後使用 'select <machine_id>' 選擇。[/yellow]")
            return
        
        console.print(f"[blue]AI 助手[/blue]: 正在處理您的請求...")
        
        result = self.agent.process_command(self.current_session, user_input)
        
        if result["success"]:
            # Show summary
            console.print(f"[green]✓ {result['summary']}[/green]")
            
            # Show detailed results
            for i, cmd_result in enumerate(result["results"], 1):
                if cmd_result["success"]:
                    if cmd_result["output"].strip():
                        console.print(Panel(
                            Syntax(cmd_result["output"], "bash", theme="monokai"),
                            title=f"指令 {i}: {cmd_result['command']}",
                            border_style="green"
                        ))
                else:
                    console.print(Panel(
                        f"[red]{cmd_result['output']}[/red]",
                        title=f"指令 {i} 失敗: {cmd_result['command']}",
                        border_style="red"
                    ))
        else:
            console.print(f"[red]✗ {result['error']}[/red]")
            
            if "suggestions" in result:
                console.print("\n[yellow]建議的指令:[/yellow]")
                for suggestion in result["suggestions"]:
                    console.print(f"• {suggestion}")
            
            if "available_commands" in result:
                console.print("\n[yellow]可用的指令類型:[/yellow]")
                for intent, description in result["available_commands"].items():
                    console.print(f"• {description}")


@click.group()
def cli():
    """SSH AI Assistant - 自然語言 SSH 指令執行助手"""
    pass


@cli.command()
def interactive():
    """啟動互動模式"""
    interface = CLIInterface()
    interface.start_interactive_mode()


@cli.command()
def machines():
    """列出所有機器"""
    interface = CLIInterface()
    interface._show_machines()


@cli.command()
@click.option('--name', prompt='機器名稱', help='機器名稱')
@click.option('--host', prompt='主機', help='SSH 主機 IP 或域名')
@click.option('--port', default=22, help='SSH 端口')
@click.option('--username', prompt='用戶名', help='SSH 用戶名')
@click.option('--password', prompt='密碼', hide_input=True, help='SSH 密碼')
@click.option('--description', default='', help='機器描述')
def add_machine(name, host, port, username, password, description):
    """添加新機器"""
    interface = CLIInterface()
    
    machine_config = {
        "id": str(uuid.uuid4()),
        "name": name,
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "description": description
    }
    
    result = interface.agent.add_machine(machine_config)
    
    if result["success"]:
        console.print(f"[green]機器添加成功！ID: {result['machine_id'][:8]}...[/green]")
    else:
        console.print(f"[red]添加機器失敗: {result['error']}[/red]")


if __name__ == "__main__":
    cli()