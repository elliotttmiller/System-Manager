"""
Remote Process Management Module
Process monitoring and management on remote devices via SSH
"""

import paramiko
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.styles import Style as PTStyle

console = Console()

# Dark theme for dialogs
PT_DARK_STYLE = PTStyle.from_dict({
    'dialog': 'bg:#1a1a1a #00d7ff',
    'dialog.body': 'bg:#1a1a1a #e0e0e0',
    'dialog frame.label': 'bg:#1a1a1a #00d7ff bold',
    'radiolist': 'bg:#1a1a1a #e0e0e0',
    'radiolist focused': 'bg:#00d7ff #000000 bold',
    'radiolist selected': 'bg:#1a1a1a #00ff87',
})


class RemoteProcessManager:
    """Comprehensive remote process management via SSH"""
    
    def __init__(self, connection_manager=None):
        self.console = console
        self.connection_manager = connection_manager
        self.ssh_client = None
    
    def connect(self, host, username, password=None, key_filename=None, port=22):
        """Establish SSH connection to remote device"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if key_filename:
                self.ssh_client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    key_filename=key_filename
                )
            else:
                self.ssh_client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    password=password
                )
            
            return {"status": "success", "message": "Connected successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def execute_command(self, command):
        """Execute command on remote device"""
        if not self.ssh_client:
            return {"status": "error", "message": "Not connected"}
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            return {
                "status": "success",
                "output": output,
                "error": error
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def list_processes(self):
        """List all running processes"""
        cmd = "ps aux --sort=-%cpu"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to list processes')}
    
    def get_process_info(self, pid):
        """Get detailed information about a process"""
        cmd = f"ps -p {pid} -o pid,ppid,user,%cpu,%mem,vsz,rss,stat,start,time,command"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Process not found')}
    
    def kill_process(self, pid, signal=15):
        """Kill a process (signal: 15=TERM, 9=KILL)"""
        cmd = f"kill -{signal} {pid}"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"status": "success", "message": f"Signal {signal} sent to process {pid}"}
        else:
            return {"status": "error", "message": result.get('error', 'Failed to kill process')}
    
    def get_top_processes(self, limit=20):
        """Get top processes by CPU usage"""
        cmd = f"ps aux --sort=-%cpu | head -n {limit + 1}"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to get top processes')}
    
    def get_process_tree(self):
        """Get process tree"""
        cmd = "pstree -p"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            # Fallback
            cmd = "ps auxf"
            result = self.execute_command(cmd)
            return {"output": result['output']} if result['status'] == "success" else {"error": "Failed to get process tree"}
    
    def search_process(self, name):
        """Search for processes by name"""
        cmd = f"ps aux | grep '{name}' | grep -v grep"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'No matching processes found')}
    
    def get_system_load(self):
        """Get system load average"""
        cmd = "uptime"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to get system load')}
    
    def list_services(self):
        """List systemd services"""
        cmd = "systemctl list-units --type=service --all"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            # Fallback for non-systemd systems
            cmd = "service --status-all"
            result = self.execute_command(cmd)
            return {"output": result['output']} if result['status'] == "success" else {"error": "Failed to list services"}
    
    def service_action(self, service_name, action):
        """Perform action on service (start/stop/restart/status)"""
        cmd = f"sudo systemctl {action} {service_name}"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"status": "success", "message": f"Service {service_name} {action} completed", "output": result['output']}
        else:
            return {"status": "error", "message": result.get('error', f'Failed to {action} service')}
    
    def disconnect(self):
        """Close SSH connection"""
        if self.ssh_client:
            self.ssh_client.close()
            return {"status": "success", "message": "Disconnected"}
        return {"status": "error", "message": "Not connected"}


def run():
    """Main entry point for remote process management"""
    manager = RemoteProcessManager()
    
    console.print(Panel.fit(
        "[bold cyan]Remote Process Management[/bold cyan]\n"
        "Manage processes and services on remote devices",
        border_style="cyan"
    ))
    
    # Get connection details
    host = console.input("[bold cyan]Enter remote host: [/bold cyan]")
    username = console.input("[bold cyan]Enter username: [/bold cyan]")
    auth_method = console.input("[bold cyan]Authentication method (password/key): [/bold cyan]")
    
    if auth_method.lower() == "password":
        from getpass import getpass
        password = getpass("Enter password: ")
        result = manager.connect(host, username, password=password)
    else:
        key_file = console.input("[bold cyan]Enter key file path: [/bold cyan]")
        result = manager.connect(host, username, key_filename=key_file)
    
    if result['status'] != "success":
        console.print(f"[red]Connection failed: {result['message']}[/red]")
        return
    
    console.print(f"[green]{result['message']}[/green]")
    
    while True:
        console.print()
        
        operation = radiolist_dialog(
            title="Process Management",
            text="Select operation:",
            values=[
                ("list", "📋  List All Processes"),
                ("top", "🔝  Top Processes (CPU)"),
                ("tree", "🌳  Process Tree"),
                ("search", "🔍  Search Process"),
                ("info", "ℹ️  Process Info"),
                ("kill", "⚠️  Kill Process"),
                ("load", "📊  System Load"),
                ("services", "🔧  List Services"),
                ("service_action", "⚙️  Service Action"),
                ("exit", "❌  Exit"),
            ],
            style=PT_DARK_STYLE,
        ).run()
        
        if operation == "list":
            console.print("\n[cyan]Fetching process list...[/cyan]")
            result = manager.list_processes()
            if 'output' in result:
                console.print(Panel(result['output'], title="All Processes", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "top":
            limit = Prompt.ask("[cyan]Number of top processes[/cyan]", default="20")
            result = manager.get_top_processes(int(limit))
            if 'output' in result:
                console.print(Panel(result['output'], title="Top Processes by CPU", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "tree":
            console.print("\n[cyan]Fetching process tree...[/cyan]")
            result = manager.get_process_tree()
            if 'output' in result:
                console.print(Panel(result['output'], title="Process Tree", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "search":
            name = Prompt.ask("[cyan]Process name to search[/cyan]")
            result = manager.search_process(name)
            if 'output' in result:
                if result['output'].strip():
                    console.print(Panel(result['output'], title=f"Search Results: {name}", border_style="cyan"))
                else:
                    console.print(f"[yellow]No processes found matching '{name}'[/yellow]")
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "info":
            pid = Prompt.ask("[cyan]Process ID (PID)[/cyan]")
            result = manager.get_process_info(pid)
            if 'output' in result:
                console.print(Panel(result['output'], title=f"Process Info: PID {pid}", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "kill":
            pid = Prompt.ask("[cyan]Process ID (PID) to kill[/cyan]")
            signal_type = radiolist_dialog(
                title="Kill Signal",
                text="Select signal type:",
                values=[
                    ("15", "TERM (15) - Graceful termination"),
                    ("9", "KILL (9) - Force kill"),
                    ("1", "HUP (1) - Hangup"),
                ],
                style=PT_DARK_STYLE,
            ).run()
            
            if signal_type and Confirm.ask(f"[yellow]Kill process {pid} with signal {signal_type}?[/yellow]", default=False):
                result = manager.kill_process(pid, int(signal_type))
                if result['status'] == "success":
                    console.print(f"[green]✓ {result['message']}[/green]")
                else:
                    console.print(f"[red]✗ {result['message']}[/red]")
        
        elif operation == "load":
            result = manager.get_system_load()
            if 'output' in result:
                console.print(Panel(result['output'], title="System Load", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "services":
            console.print("\n[cyan]Fetching service list...[/cyan]")
            result = manager.list_services()
            if 'output' in result:
                console.print(Panel(result['output'], title="System Services", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "service_action":
            service_name = Prompt.ask("[cyan]Service name[/cyan]")
            action = radiolist_dialog(
                title="Service Action",
                text="Select action:",
                values=[
                    ("status", "ℹ️  Status"),
                    ("start", "▶️  Start"),
                    ("stop", "⏹️  Stop"),
                    ("restart", "🔄  Restart"),
                ],
                style=PT_DARK_STYLE,
            ).run()
            
            if action:
                result = manager.service_action(service_name, action)
                if result['status'] == "success":
                    console.print(f"[green]✓ {result['message']}[/green]")
                    if result.get('output'):
                        console.print(Panel(result['output'], title=f"Service {action} output", border_style="green"))
                else:
                    console.print(f"[red]✗ {result['message']}[/red]")
        
        elif operation == "exit" or operation is None:
            break
    
    manager.disconnect()
    console.print("[green]Disconnected from remote device[/green]")
    Prompt.ask("\nPress Enter to continue")


if __name__ == "__main__":
    run()
