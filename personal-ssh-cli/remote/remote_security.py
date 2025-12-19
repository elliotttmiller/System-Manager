"""
Remote Security Tools Module
Security scanning and hardening on remote devices via SSH
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


class RemoteSecurityTools:
    """Comprehensive remote security tools via SSH"""
    
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
    
    def scan_open_ports(self):
        """Scan for open ports"""
        cmd = "ss -tulpn || netstat -tulpn"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to scan ports')}
    
    def check_firewall_status(self):
        """Check firewall status"""
        cmd = "sudo ufw status verbose || sudo iptables -L -n -v || sudo firewall-cmd --state"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to check firewall')}
    
    def list_sudo_users(self):
        """List users with sudo privileges"""
        cmd = "getent group sudo wheel | cut -d: -f4"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to list sudo users')}
    
    def check_failed_logins(self):
        """Check failed login attempts"""
        cmd = "sudo lastb -n 50 || sudo cat /var/log/auth.log | grep 'Failed password'"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to check login attempts')}
    
    def check_ssh_config(self):
        """Check SSH configuration"""
        cmd = "sudo cat /etc/ssh/sshd_config | grep -v '^#' | grep -v '^$'"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to check SSH config')}
    
    def list_cron_jobs(self):
        """List all cron jobs"""
        cmd = "sudo cat /etc/crontab; for user in $(cut -f1 -d: /etc/passwd); do echo \"Cron for $user:\"; sudo crontab -u $user -l 2>/dev/null; done"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to list cron jobs')}
    
    def check_setuid_files(self):
        """Find SETUID/SETGID files"""
        cmd = "sudo find / -type f \\( -perm -4000 -o -perm -2000 \\) -ls 2>/dev/null | head -n 100"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to check SETUID files')}
    
    def check_world_writable(self):
        """Find world-writable files"""
        cmd = "sudo find / -type f -perm -002 -ls 2>/dev/null | head -n 100"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to check world-writable files')}
    
    def check_listening_services(self):
        """Check listening services"""
        cmd = "sudo ss -tulpn | grep LISTEN"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to check listening services')}
    
    def check_system_updates(self):
        """Check for system updates"""
        cmd = "sudo apt update && apt list --upgradable 2>/dev/null || sudo yum check-update"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to check updates')}
    
    def view_security_logs(self):
        """View security-related logs"""
        cmd = "sudo tail -n 100 /var/log/auth.log || sudo tail -n 100 /var/log/secure"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to view logs')}
    
    def check_password_policy(self):
        """Check password policy"""
        cmd = "sudo cat /etc/login.defs | grep -E 'PASS_MAX_DAYS|PASS_MIN_DAYS|PASS_WARN_AGE|PASS_MIN_LEN'"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to check password policy')}
    
    def list_users(self):
        """List all system users"""
        cmd = "cat /etc/passwd | cut -d: -f1,3,6,7"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to list users')}
    
    def check_rootkit(self):
        """Basic rootkit check"""
        cmd = "sudo chkrootkit || sudo rkhunter --check --skip-keypress"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": "Rootkit scanner not installed (install chkrootkit or rkhunter)"}
    
    def disconnect(self):
        """Close SSH connection"""
        if self.ssh_client:
            self.ssh_client.close()
            return {"status": "success", "message": "Disconnected"}
        return {"status": "error", "message": "Not connected"}


def run():
    """Main entry point for remote security tools"""
    tools = RemoteSecurityTools()
    
    console.print(Panel.fit(
        "[bold cyan]Remote Security Tools[/bold cyan]\n"
        "Security scanning and hardening on remote devices",
        border_style="cyan"
    ))
    
    # Get connection details
    host = console.input("[bold cyan]Enter remote host: [/bold cyan]")
    username = console.input("[bold cyan]Enter username: [/bold cyan]")
    auth_method = console.input("[bold cyan]Authentication method (password/key): [/bold cyan]")
    
    if auth_method.lower() == "password":
        from getpass import getpass
        password = getpass("Enter password: ")
        result = tools.connect(host, username, password=password)
    else:
        key_file = console.input("[bold cyan]Enter key file path: [/bold cyan]")
        result = tools.connect(host, username, key_filename=key_file)
    
    if result['status'] != "success":
        console.print(f"[red]Connection failed: {result['message']}[/red]")
        return
    
    console.print(f"[green]{result['message']}[/green]")
    
    while True:
        console.print()
        
        operation = radiolist_dialog(
            title="Security Tools",
            text="Select security check:",
            values=[
                ("ports", "🔌  Scan Open Ports"),
                ("firewall", "🔒  Firewall Status"),
                ("sudo_users", "👥  Sudo Users"),
                ("failed_logins", "🚫  Failed Logins"),
                ("ssh_config", "🔐  SSH Configuration"),
                ("cron", "⏰  Cron Jobs"),
                ("setuid", "⚠️  SETUID Files"),
                ("writable", "📝  World-Writable Files"),
                ("services", "🔧  Listening Services"),
                ("updates", "📦  System Updates"),
                ("logs", "📋  Security Logs"),
                ("password", "🔑  Password Policy"),
                ("users", "👤  List Users"),
                ("rootkit", "🦠  Rootkit Check"),
                ("exit", "❌  Exit"),
            ],
            style=PT_DARK_STYLE,
        ).run()
        
        if operation == "ports":
            console.print("\n[cyan]Scanning open ports...[/cyan]")
            result = tools.scan_open_ports()
            if 'output' in result:
                console.print(Panel(result['output'], title="Open Ports", border_style="yellow"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "firewall":
            result = tools.check_firewall_status()
            if 'output' in result:
                console.print(Panel(result['output'], title="Firewall Status", border_style="green"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "sudo_users":
            result = tools.list_sudo_users()
            if 'output' in result:
                console.print(Panel(result['output'], title="Users with Sudo Privileges", border_style="yellow"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "failed_logins":
            console.print("\n[cyan]Checking failed login attempts...[/cyan]")
            result = tools.check_failed_logins()
            if 'output' in result:
                console.print(Panel(result['output'], title="Failed Login Attempts", border_style="red"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "ssh_config":
            result = tools.check_ssh_config()
            if 'output' in result:
                console.print(Panel(result['output'], title="SSH Configuration", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "cron":
            console.print("\n[cyan]Fetching cron jobs...[/cyan]")
            result = tools.list_cron_jobs()
            if 'output' in result:
                console.print(Panel(result['output'], title="Cron Jobs", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "setuid":
            console.print("\n[cyan]Searching for SETUID/SETGID files...[/cyan]")
            result = tools.check_setuid_files()
            if 'output' in result:
                console.print(Panel(result['output'], title="SETUID/SETGID Files", border_style="yellow"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "writable":
            console.print("\n[cyan]Searching for world-writable files...[/cyan]")
            result = tools.check_world_writable()
            if 'output' in result:
                console.print(Panel(result['output'], title="World-Writable Files", border_style="red"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "services":
            result = tools.check_listening_services()
            if 'output' in result:
                console.print(Panel(result['output'], title="Listening Services", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "updates":
            console.print("\n[cyan]Checking for system updates...[/cyan]")
            result = tools.check_system_updates()
            if 'output' in result:
                console.print(Panel(result['output'], title="Available Updates", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "logs":
            console.print("\n[cyan]Fetching security logs...[/cyan]")
            result = tools.view_security_logs()
            if 'output' in result:
                console.print(Panel(result['output'], title="Security Logs", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "password":
            result = tools.check_password_policy()
            if 'output' in result:
                console.print(Panel(result['output'], title="Password Policy", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "users":
            result = tools.list_users()
            if 'output' in result:
                console.print(Panel(result['output'], title="System Users", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "rootkit":
            console.print("\n[cyan]Running rootkit check (this may take time)...[/cyan]")
            result = tools.check_rootkit()
            if 'output' in result:
                console.print(Panel(result['output'], title="Rootkit Scan Results", border_style="green"))
            else:
                console.print(f"[yellow]Warning: {result.get('error')}[/yellow]")
        
        elif operation == "exit" or operation is None:
            break
    
    tools.disconnect()
    console.print("[green]Disconnected from remote device[/green]")
    Prompt.ask("\nPress Enter to continue")


if __name__ == "__main__":
    run()
