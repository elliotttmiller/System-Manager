"""
Remote Service Monitor
Monitor and manage services on remote desktop via SSH
"""

import paramiko
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

console = Console()


class RemoteServiceMonitor:
    """Monitor and manage services on remote device via SSH"""
    
    def __init__(self, connection_manager=None):
        self.console = console
        self.connection_manager = connection_manager
        self.device_info = {}
        
    def set_connection(self, connection_manager, connection_id):
        """Set SSH connection using ConnectionManager."""
        connection = connection_manager.get_connection(connection_id)
        if not connection:
            raise ValueError(f"Connection '{connection_id}' not found")

        self.connection_manager = connection_manager
        self.device_info = {
            "host": connection.profile.get("hostname"),
            "username": connection.profile.get("username"),
            "port": connection.profile.get("port", 22),
        }

    def execute_command(self, connection_id, command, timeout=30):
        """Execute command on remote device using ConnectionManager."""
        connection = self.connection_manager.get_connection(connection_id)
        if not connection:
            return {"status": "error", "message": f"Connection '{connection_id}' not found"}

        try:
            result = connection.execute_command(command, timeout=timeout)
            return {
                "status": "success" if result.get("exit_code") == 0 else "error",
                "output": result.get("output"),
                "error": result.get("error"),
                "exit_code": result.get("exit_code"),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
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
                    key_filename=key_filename,
                    timeout=10
                )
            else:
                self.ssh_client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    password=password,
                    timeout=10
                )
            
            self.device_info = {
                "host": host,
                "username": username,
                "port": port
            }
            
            return {"status": "success", "message": "Connected successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def detect_os(self):
        """Detect operating system of remote device"""
        result = self.execute_command("uname -s")
        
        if result["status"] == "success":
            os_name = result["output"].strip().lower()
            if "linux" in os_name:
                return "Linux"
            elif "darwin" in os_name:
                return "Darwin"
            else:
                return os_name
        
        # Try Windows detection
        result = self.execute_command("echo %OS%")
        if "Windows" in result.get("output", ""):
            return "Windows"
        
        return "Unknown"
    
    def check_service_status(self, service_name):
        """Check if a service is running on remote device"""
        os_type = self.detect_os()
        
        try:
            if os_type == "Linux":
                # Check systemd service
                result = self.execute_command(f"systemctl is-active {service_name}")
                running = result["output"].strip() == "active"
                
                # Get detailed status
                status_result = self.execute_command(f"systemctl status {service_name}")
                
                return {
                    "running": running,
                    "status": result["output"].strip(),
                    "details": status_result["output"]
                }
                
            elif os_type == "Darwin":
                # macOS service check
                result = self.execute_command(f"launchctl list | grep {service_name}")
                running = result["exit_code"] == 0
                
                return {
                    "running": running,
                    "status": "active" if running else "inactive",
                    "details": result["output"]
                }
                
            elif os_type == "Windows":
                # Windows service check
                result = self.execute_command(f"powershell Get-Service -Name {service_name} | Select-Object -Property Status")
                running = "Running" in result["output"]
                
                return {
                    "running": running,
                    "status": "running" if running else "stopped",
                    "details": result["output"]
                }
                
            else:
                return {
                    "running": False,
                    "status": "unknown",
                    "details": f"Unsupported OS: {os_type}"
                }
                
        except Exception as e:
            return {
                "running": False,
                "status": "error",
                "details": str(e)
            }
    
    def start_service(self, service_name):
        """Start a service on remote device"""
        os_type = self.detect_os()
        
        try:
            if os_type == "Linux":
                result = self.execute_command(f"sudo systemctl start {service_name}")
                success = result["exit_code"] == 0
                
                # Enable service to start on boot
                if success:
                    self.execute_command(f"sudo systemctl enable {service_name}")
                
                return {
                    "success": success,
                    "message": "Service started successfully" if success else result["error"]
                }
                
            elif os_type == "Darwin":
                result = self.execute_command(f"sudo launchctl load /Library/LaunchDaemons/{service_name}.plist")
                success = result["exit_code"] == 0
                
                return {
                    "success": success,
                    "message": "Service started successfully" if success else result["error"]
                }
                
            elif os_type == "Windows":
                result = self.execute_command(f"powershell Start-Service {service_name}")
                success = result["exit_code"] == 0
                
                return {
                    "success": success,
                    "message": "Service started successfully" if success else result["error"]
                }
                
            else:
                return {"success": False, "message": f"Unsupported OS: {os_type}"}
                
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def stop_service(self, service_name):
        """Stop a service on remote device"""
        os_type = self.detect_os()
        
        try:
            if os_type == "Linux":
                result = self.execute_command(f"sudo systemctl stop {service_name}")
                success = result["exit_code"] == 0
                
            elif os_type == "Darwin":
                result = self.execute_command(f"sudo launchctl unload /Library/LaunchDaemons/{service_name}.plist")
                success = result["exit_code"] == 0
                
            elif os_type == "Windows":
                result = self.execute_command(f"powershell Stop-Service {service_name}")
                success = result["exit_code"] == 0
                
            else:
                return {"success": False, "message": f"Unsupported OS: {os_type}"}
            
            return {
                "success": success,
                "message": "Service stopped successfully" if success else result.get("error", "Failed")
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def restart_service(self, service_name):
        """Restart a service on remote device"""
        os_type = self.detect_os()
        
        try:
            if os_type == "Linux":
                result = self.execute_command(f"sudo systemctl restart {service_name}")
                
            elif os_type == "Darwin":
                self.stop_service(service_name)
                time.sleep(2)
                return self.start_service(service_name)
                
            elif os_type == "Windows":
                result = self.execute_command(f"powershell Restart-Service {service_name}")
                
            else:
                return {"success": False, "message": f"Unsupported OS: {os_type}"}
            
            success = result["exit_code"] == 0
            return {
                "success": success,
                "message": "Service restarted successfully" if success else result.get("error", "Failed")
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def list_all_services(self):
        """List all services on remote device"""
        os_type = self.detect_os()
        
        try:
            if os_type == "Linux":
                result = self.execute_command("systemctl list-units --type=service --all")
                
            elif os_type == "Darwin":
                result = self.execute_command("launchctl list")
                
            elif os_type == "Windows":
                result = self.execute_command("powershell Get-Service | Format-Table -AutoSize")
                
            else:
                return {"success": False, "message": f"Unsupported OS: {os_type}"}
            
            return {
                "success": result["exit_code"] == 0,
                "services": result["output"],
                "os": os_type
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def check_ssh_server(self):
        """Check SSH server status on remote device"""
        os_type = self.detect_os()
        
        if os_type == "Linux":
            service_names = ["ssh", "sshd"]
        elif os_type == "Darwin":
            service_names = ["com.openssh.sshd"]
        elif os_type == "Windows":
            service_names = ["sshd"]
        else:
            return {"running": False, "message": "Unsupported OS"}
        
        # Try each possible service name
        for service in service_names:
            status = self.check_service_status(service)
            if status["running"]:
                return {
                    "running": True,
                    "service_name": service,
                    "status": status
                }
        
        return {"running": False, "message": "SSH service not found"}
    
    def get_system_uptime(self):
        """Get system uptime"""
        result = self.execute_command("uptime")
        
        if result["status"] == "success":
            return {
                "success": True,
                "uptime": result["output"].strip()
            }
        
        return {"success": False, "message": "Could not get uptime"}
    
    def get_system_load(self):
        """Get system load average"""
        os_type = self.detect_os()
        
        if os_type in ["Linux", "Darwin"]:
            result = self.execute_command("cat /proc/loadavg 2>/dev/null || uptime | awk -F'load average:' '{print $2}'")
            
            if result["status"] == "success":
                return {
                    "success": True,
                    "load": result["output"].strip()
                }
        
        elif os_type == "Windows":
            result = self.execute_command("powershell Get-WmiObject Win32_Processor | Select-Object -Property LoadPercentage")
            
            if result["status"] == "success":
                return {
                    "success": True,
                    "load": result["output"].strip()
                }
        
        return {"success": False, "message": "Could not get load"}
    
    def display_service_status(self, service_name):
        """Display comprehensive service status"""
        console.clear()
        
        with console.status(f"[cyan]Checking {service_name} status...[/cyan]"):
            status = self.check_service_status(service_name)
            os_type = self.detect_os()
        
        # Create status table
        table = Table(title=f"Service Status: {service_name}", show_header=True, header_style="bold magenta")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Service Name", service_name)
        table.add_row("Remote Host", self.device_info.get("host", "Unknown"))
        table.add_row("Operating System", os_type)
        
        running = status["running"]
        status_icon = "✓" if running else "✗"
        status_color = "green" if running else "red"
        
        table.add_row("Status", f"[{status_color}]{status_icon} {status['status'].upper()}[/{status_color}]")
        
        console.print(table)
        
        # Display details
        if status.get("details"):
            details_panel = Panel(
                status["details"],
                title="Service Details",
                border_style="blue"
            )
            console.print("\n")
            console.print(details_panel)
        
        return status
    
    def monitor_services(self, services, interval=60):
        """Continuously monitor multiple services"""
        console.print(Panel(
            f"[green]Remote Service Monitor Started[/green]\n"
            f"Monitoring: {', '.join(services)}\n"
            f"Check Interval: {interval} seconds\n"
            f"Press Ctrl+C to stop",
            title="Remote Monitor",
            border_style="blue"
        ))
        
        try:
            while True:
                console.clear()
                
                # Create monitoring table
                table = Table(title="Remote Services Status", show_header=True, header_style="bold magenta")
                table.add_column("Service", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Last Check", style="yellow")
                
                for service in services:
                    status = self.check_service_status(service)
                    running = status["running"]
                    status_icon = "✓" if running else "✗"
                    status_color = "green" if running else "red"
                    
                    table.add_row(
                        service,
                        f"[{status_color}]{status_icon} {status['status'].upper()}[/{status_color}]",
                        datetime.now().strftime("%H:%M:%S")
                    )
                
                console.print(table)
                
                # System info
                uptime = self.get_system_uptime()
                if uptime["success"]:
                    console.print(f"\n[cyan]System Uptime:[/cyan] {uptime['uptime']}")
                
                console.print(f"\n[dim]Next check in {interval} seconds...[/dim]")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Remote service monitor stopped by user[/yellow]")
    
    def disconnect(self):
        """Close SSH connection"""
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None


def run(connection_manager=None):
    """Entry point for remote service monitor"""
    monitor = RemoteServiceMonitor(connection_manager)
    
    if not connection_manager:
        console.print("[red]Error: No connection manager available[/red]")
        console.print("[yellow]Please connect to a device first[/yellow]")
        console.input("\n[dim]Press Enter to continue...[/dim]")
        return
    
    # Get the first active connection
    connections = connection_manager.list_connections()
    active_connections = [conn for conn in connections if conn.get('connected')]
    
    if not active_connections:
        console.print("[red]Error: No active SSH connection[/red]")
        console.print("[yellow]Please connect to a device first[/yellow]")
        console.input("\n[dim]Press Enter to continue...[/dim]")
        return
    
    # Use the first active connection
    connection_id = active_connections[0]['id']
    ssh_connection = connection_manager.get_connection(connection_id)
    
    if not ssh_connection or not ssh_connection.client:
        console.print("[red]Error: Invalid SSH connection[/red]")
        console.input("\n[dim]Press Enter to continue...[/dim]")
        return
    
    # Set connection with the SSH client from the connection object
    device_info = {
        'host': active_connections[0].get('hostname'),
        'username': active_connections[0].get('username'),
        'port': ssh_connection.profile.get('port', 22)
    }
    monitor.set_connection(ssh_connection.client, device_info)
    
    while True:
        console.clear()
        console.print(Panel(
            f"[bold cyan]Remote Service Monitor[/bold cyan]\n"
            f"Connected to: {monitor.device_info.get('host', 'Unknown')}\n"
            f"OS: {monitor.detect_os()}",
            border_style="cyan"
        ))
        
        console.print("\n[bold]Options:[/bold]")
        console.print("1. Check Service Status")
        console.print("2. Start Service")
        console.print("3. Stop Service")
        console.print("4. Restart Service")
        console.print("5. List All Services")
        console.print("6. Check SSH Server")
        console.print("7. Monitor Services (Continuous)")
        console.print("8. System Information")
        console.print("0. Back")
        
        choice = console.input("\n[cyan]Select option:[/cyan] ").strip()
        
        if choice == "1":
            service = console.input("[cyan]Enter service name:[/cyan] ").strip()
            if service:
                monitor.display_service_status(service)
                console.input("\n[dim]Press Enter to continue...[/dim]")
                
        elif choice == "2":
            service = console.input("[cyan]Enter service name:[/cyan] ").strip()
            if service:
                with console.status("[cyan]Starting service...[/cyan]"):
                    result = monitor.start_service(service)
                
                if result["success"]:
                    console.print(f"\n[green]✓ {result['message']}[/green]")
                else:
                    console.print(f"\n[red]✗ {result['message']}[/red]")
                console.input("\n[dim]Press Enter to continue...[/dim]")
                
        elif choice == "3":
            service = console.input("[cyan]Enter service name:[/cyan] ").strip()
            if service:
                with console.status("[cyan]Stopping service...[/cyan]"):
                    result = monitor.stop_service(service)
                
                if result["success"]:
                    console.print(f"\n[green]✓ {result['message']}[/green]")
                else:
                    console.print(f"\n[red]✗ {result['message']}[/red]")
                console.input("\n[dim]Press Enter to continue...[/dim]")
                
        elif choice == "4":
            service = console.input("[cyan]Enter service name:[/cyan] ").strip()
            if service:
                with console.status("[cyan]Restarting service...[/cyan]"):
                    result = monitor.restart_service(service)
                
                if result["success"]:
                    console.print(f"\n[green]✓ {result['message']}[/green]")
                else:
                    console.print(f"\n[red]✗ {result['message']}[/red]")
                console.input("\n[dim]Press Enter to continue...[/dim]")
                
        elif choice == "5":
            with console.status("[cyan]Loading services...[/cyan]"):
                result = monitor.list_all_services()
            
            if result["success"]:
                console.print(Panel(
                    result["services"],
                    title=f"Services on {result['os']}",
                    border_style="blue"
                ))
            else:
                console.print(f"\n[red]✗ {result['message']}[/red]")
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
        elif choice == "6":
            with console.status("[cyan]Checking SSH server...[/cyan]"):
                result = monitor.check_ssh_server()
            
            if result["running"]:
                console.print(f"\n[green]✓ SSH Server is running[/green]")
                console.print(f"Service: {result['service_name']}")
            else:
                console.print(f"\n[yellow]✗ {result['message']}[/yellow]")
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
        elif choice == "7":
            services_input = console.input("[cyan]Enter services to monitor (comma-separated):[/cyan] ").strip()
            if services_input:
                services = [s.strip() for s in services_input.split(",")]
                interval = console.input("[cyan]Check interval in seconds (default 60):[/cyan] ").strip()
                interval = int(interval) if interval.isdigit() else 60
                monitor.monitor_services(services, interval)
                
        elif choice == "8":
            with console.status("[cyan]Getting system information...[/cyan]"):
                uptime = monitor.get_system_uptime()
                load = monitor.get_system_load()
            
            console.print("\n[bold]System Information:[/bold]")
            if uptime["success"]:
                console.print(f"[cyan]Uptime:[/cyan] {uptime['uptime']}")
            if load["success"]:
                console.print(f"[cyan]Load:[/cyan] {load['load']}")
            
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
        elif choice == "0":
            break


if __name__ == "__main__":
    run()
