"""
Remote System Monitoring Module
Monitor remote device resources, performance, and health via SSH
"""

import paramiko
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
import json
from datetime import datetime

console = Console()


class RemoteSystemMonitor:
    """Comprehensive remote system monitoring via SSH"""
    
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
    
    def get_remote_system_info(self):
        """Get comprehensive remote system information"""
        commands = {
            "Hostname": "hostname",
            "Kernel": "uname -r",
            "OS": "cat /etc/os-release | grep PRETTY_NAME | cut -d'\"' -f2",
            "Uptime": "uptime -p",
            "CPU Model": "lscpu | grep 'Model name' | cut -d':' -f2 | xargs",
            "CPU Cores": "nproc",
            "Total RAM": "free -h | grep Mem | awk '{print $2}'",
            "Architecture": "uname -m"
        }
        
        system_info = {}
        
        for key, cmd in commands.items():
            result = self.execute_command(cmd)
            if result['status'] == "success":
                system_info[key] = result['output'].strip()
            else:
                system_info[key] = "N/A"
        
        return system_info
    
    def get_remote_cpu_usage(self):
        """Get remote CPU usage statistics"""
        # CPU usage
        cmd = "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/' | awk '{print 100 - $1}'"
        result = self.execute_command(cmd)
        
        cpu_usage = result['output'].strip() if result['status'] == "success" else "N/A"
        
        # Load average
        result = self.execute_command("cat /proc/loadavg")
        load_avg = result['output'].strip() if result['status'] == "success" else "N/A"
        
        return {
            "CPU Usage": f"{cpu_usage}%",
            "Load Average": load_avg
        }
    
    def get_remote_memory_usage(self):
        """Get remote memory usage statistics"""
        result = self.execute_command("free -h")
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result['message']}
    
    def get_remote_disk_usage(self):
        """Get remote disk usage"""
        result = self.execute_command("df -h")
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result['message']}
    
    def get_remote_network_stats(self):
        """Get remote network statistics"""
        result = self.execute_command("ifconfig || ip addr")
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result['message']}
    
    def get_remote_top_processes(self):
        """Get top processes on remote device"""
        cmd = "ps aux --sort=-%cpu | head -n 11"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result['message']}
    
    def get_remote_services_status(self):
        """Get status of remote services"""
        cmd = "systemctl list-units --type=service --state=running"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            # Fallback for non-systemd systems
            result = self.execute_command("service --status-all")
            return {"output": result['output']} if result['status'] == "success" else {"error": result['message']}
    
    def disconnect(self):
        """Close SSH connection"""
        if self.ssh_client:
            self.ssh_client.close()
            return {"status": "success", "message": "Disconnected"}
        return {"status": "error", "message": "Not connected"}


def run():
    """Main entry point for remote system monitoring"""
    monitor = RemoteSystemMonitor()
    
    console.print(Panel.fit(
        "[bold cyan]Remote System Monitoring[/bold cyan]\n"
        "Monitor remote devices via SSH",
        border_style="cyan"
    ))
    
    # Get connection details
    host = console.input("[bold cyan]Enter remote host: [/bold cyan]")
    username = console.input("[bold cyan]Enter username: [/bold cyan]")
    auth_method = console.input("[bold cyan]Authentication method (password/key): [/bold cyan]")
    
    if auth_method.lower() == "password":
        from getpass import getpass
        password = getpass("Enter password: ")
        result = monitor.connect(host, username, password=password)
    else:
        key_file = console.input("[bold cyan]Enter key file path: [/bold cyan]")
        result = monitor.connect(host, username, key_filename=key_file)
    
    if result['status'] != "success":
        console.print(f"[red]Connection failed: {result['message']}[/red]")
        return
    
    console.print(f"[green]{result['message']}[/green]")
    
    options = [
        "1. System Overview",
        "2. CPU Usage",
        "3. Memory Usage",
        "4. Disk Usage",
        "5. Network Statistics",
        "6. Top Processes",
        "7. Services Status",
        "8. Execute Custom Command",
        "0. Disconnect and Exit"
    ]
    
    while True:
        console.print("\n[bold cyan]Remote Monitoring Menu:[/bold cyan]")
        for option in options:
            console.print(f"  {option}")
        
        choice = console.input("\n[bold yellow]Enter your choice: [/bold yellow]")
        
        if choice == "0":
            monitor.disconnect()
            console.print("[green]Disconnected[/green]")
            break
        
        elif choice == "1":
            console.print("[yellow]Fetching system information...[/yellow]")
            info = monitor.get_remote_system_info()
            
            table = Table(title="Remote System Information", style="cyan")
            table.add_column("Property", style="bold yellow")
            table.add_column("Value", style="green")
            
            for key, value in info.items():
                table.add_row(key, value)
            
            console.print(table)
        
        elif choice == "2":
            console.print("[yellow]Fetching CPU usage...[/yellow]")
            cpu_info = monitor.get_remote_cpu_usage()
            
            table = Table(title="Remote CPU Usage", style="cyan")
            table.add_column("Metric", style="bold yellow")
            table.add_column("Value", style="green")
            
            for key, value in cpu_info.items():
                table.add_row(key, value)
            
            console.print(table)
        
        elif choice == "3":
            console.print("[yellow]Fetching memory usage...[/yellow]")
            mem_info = monitor.get_remote_memory_usage()
            
            if 'output' in mem_info:
                console.print(Panel.fit(mem_info['output'], title="Remote Memory Usage", border_style="cyan"))
            else:
                console.print(f"[red]Error: {mem_info['error']}[/red]")
        
        elif choice == "4":
            console.print("[yellow]Fetching disk usage...[/yellow]")
            disk_info = monitor.get_remote_disk_usage()
            
            if 'output' in disk_info:
                console.print(Panel.fit(disk_info['output'], title="Remote Disk Usage", border_style="cyan"))
            else:
                console.print(f"[red]Error: {disk_info['error']}[/red]")
        
        elif choice == "5":
            console.print("[yellow]Fetching network statistics...[/yellow]")
            net_info = monitor.get_remote_network_stats()
            
            if 'output' in net_info:
                console.print(Panel.fit(net_info['output'], title="Remote Network Statistics", border_style="cyan"))
            else:
                console.print(f"[red]Error: {net_info['error']}[/red]")
        
        elif choice == "6":
            console.print("[yellow]Fetching top processes...[/yellow]")
            proc_info = monitor.get_remote_top_processes()
            
            if 'output' in proc_info:
                console.print(Panel.fit(proc_info['output'], title="Remote Top Processes", border_style="cyan"))
            else:
                console.print(f"[red]Error: {proc_info['error']}[/red]")
        
        elif choice == "7":
            console.print("[yellow]Fetching services status...[/yellow]")
            services_info = monitor.get_remote_services_status()
            
            if 'output' in services_info:
                console.print(Panel.fit(services_info['output'], title="Remote Services Status", border_style="cyan"))
            else:
                console.print(f"[red]Error: {services_info['error']}[/red]")
        
        elif choice == "8":
            command = console.input("[bold cyan]Enter command to execute: [/bold cyan]")
            console.print("[yellow]Executing command...[/yellow]")
            result = monitor.execute_command(command)
            
            if result['status'] == "success":
                console.print(Panel.fit(
                    f"Output:\n{result['output']}\n\nErrors:\n{result['error']}",
                    title="Command Result",
                    border_style="green"
                ))
            else:
                console.print(f"[red]Error: {result['message']}[/red]")
        
        console.input("\n[bold yellow]Press Enter to continue...[/bold yellow]")


if __name__ == "__main__":
    run()
