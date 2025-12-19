"""
Remote Server Actions
Comprehensive SSH/SSHD server management for remote desktop
Provides start, stop, restart, and advanced configuration management
"""

import paramiko
import time
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

console = Console()


class RemoteServerActions:
    """Manage SSH/SSHD server on remote desktop"""
    
    def __init__(self, connection_manager=None):
        self.console = console
        self.connection_manager = connection_manager
        self.ssh_client = None
        self.device_info = {}
        self.os_type = None
        
    def set_connection(self, ssh_client, device_info=None):
        """Set SSH connection from connection manager"""
        self.ssh_client = ssh_client
        self.device_info = device_info or {}
        self.os_type = self.detect_os()
        
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
            self.os_type = self.detect_os()
            
            return {"status": "success", "message": "Connected successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def execute_command(self, command, timeout=30, use_sudo=False):
        """Execute command on remote device"""
        if not self.ssh_client:
            return {"status": "error", "message": "Not connected to remote device"}
        
        try:
            if use_sudo and not command.startswith("sudo"):
                command = f"sudo {command}"
            
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            exit_code = stdout.channel.recv_exit_status()
            
            return {
                "status": "success" if exit_code == 0 else "error",
                "output": output,
                "error": error,
                "exit_code": exit_code
            }
        except Exception as e:
            return {"status": "error", "message": str(e), "output": "", "error": str(e)}
    
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
    
    def get_ssh_service_name(self):
        """Get the correct SSH service name based on OS"""
        if self.os_type == "Linux":
            # Check which service exists
            for service in ["sshd", "ssh"]:
                result = self.execute_command(f"systemctl list-units --type=service --all | grep {service}")
                if result["exit_code"] == 0:
                    return service
            return "sshd"  # Default
        elif self.os_type == "Darwin":
            return "com.openssh.sshd"
        elif self.os_type == "Windows":
            return "sshd"
        return "sshd"
    
    def check_ssh_status(self):
        """Check SSH server status with detailed information"""
        service_name = self.get_ssh_service_name()
        
        try:
            if self.os_type == "Linux":
                # Get service status
                status_result = self.execute_command(f"systemctl status {service_name}")
                is_active = self.execute_command(f"systemctl is-active {service_name}")
                is_enabled = self.execute_command(f"systemctl is-enabled {service_name}")
                
                # Get listening ports
                port_result = self.execute_command("ss -tlnp | grep ssh || netstat -tlnp | grep ssh")
                
                # Get process info
                process_result = self.execute_command("ps aux | grep sshd | grep -v grep")
                
                return {
                    "running": is_active["output"].strip() == "active",
                    "enabled": is_enabled["output"].strip() == "enabled",
                    "status_output": status_result["output"],
                    "ports": port_result["output"],
                    "processes": process_result["output"],
                    "service_name": service_name
                }
                
            elif self.os_type == "Darwin":
                result = self.execute_command(f"launchctl list | grep {service_name}")
                status = self.execute_command("systemsetup -getremotelogin")
                
                return {
                    "running": result["exit_code"] == 0,
                    "enabled": "On" in status["output"],
                    "status_output": status["output"],
                    "ports": self.execute_command("lsof -i :22")["output"],
                    "processes": self.execute_command("ps aux | grep sshd | grep -v grep")["output"],
                    "service_name": service_name
                }
                
            elif self.os_type == "Windows":
                result = self.execute_command(f"powershell Get-Service -Name {service_name} | Format-List *")
                
                return {
                    "running": "Running" in result["output"],
                    "enabled": "Automatic" in result["output"],
                    "status_output": result["output"],
                    "ports": self.execute_command("netstat -an | findstr :22")["output"],
                    "processes": self.execute_command("tasklist | findstr sshd")["output"],
                    "service_name": service_name
                }
                
            else:
                return {
                    "running": False,
                    "enabled": False,
                    "status_output": f"Unsupported OS: {self.os_type}",
                    "service_name": service_name
                }
                
        except Exception as e:
            return {
                "running": False,
                "enabled": False,
                "status_output": f"Error: {str(e)}",
                "service_name": service_name
            }
    
    def start_ssh_server(self):
        """Start SSH server on remote device"""
        service_name = self.get_ssh_service_name()
        
        try:
            if self.os_type == "Linux":
                result = self.execute_command(f"sudo systemctl start {service_name}")
                
                if result["exit_code"] == 0:
                    # Verify it started
                    time.sleep(1)
                    status = self.check_ssh_status()
                    return {
                        "success": status["running"],
                        "message": "SSH server started successfully" if status["running"] else "Failed to verify startup",
                        "details": result["output"]
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to start SSH server",
                        "details": result["error"]
                    }
                    
            elif self.os_type == "Darwin":
                result = self.execute_command("sudo systemsetup -setremotelogin on")
                return {
                    "success": result["exit_code"] == 0,
                    "message": "SSH server started successfully" if result["exit_code"] == 0 else "Failed to start",
                    "details": result["output"]
                }
                
            elif self.os_type == "Windows":
                result = self.execute_command(f"powershell Start-Service {service_name}")
                return {
                    "success": result["exit_code"] == 0,
                    "message": "SSH server started successfully" if result["exit_code"] == 0 else "Failed to start",
                    "details": result["output"]
                }
                
            else:
                return {"success": False, "message": f"Unsupported OS: {self.os_type}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def stop_ssh_server(self):
        """Stop SSH server on remote device"""
        service_name = self.get_ssh_service_name()
        
        # Warning: Stopping SSH might disconnect us
        console.print("[yellow]⚠️  Warning: Stopping SSH server will disconnect this session![/yellow]")
        if not Confirm.ask("Are you sure you want to continue?"):
            return {"success": False, "message": "Operation cancelled by user"}
        
        try:
            if self.os_type == "Linux":
                result = self.execute_command(f"sudo systemctl stop {service_name}")
                return {
                    "success": result["exit_code"] == 0,
                    "message": "SSH server stopped" if result["exit_code"] == 0 else "Failed to stop",
                    "details": result["output"]
                }
                
            elif self.os_type == "Darwin":
                result = self.execute_command("sudo systemsetup -setremotelogin off")
                return {
                    "success": result["exit_code"] == 0,
                    "message": "SSH server stopped" if result["exit_code"] == 0 else "Failed to stop",
                    "details": result["output"]
                }
                
            elif self.os_type == "Windows":
                result = self.execute_command(f"powershell Stop-Service {service_name}")
                return {
                    "success": result["exit_code"] == 0,
                    "message": "SSH server stopped" if result["exit_code"] == 0 else "Failed to stop",
                    "details": result["output"]
                }
                
            else:
                return {"success": False, "message": f"Unsupported OS: {self.os_type}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def restart_ssh_server(self):
        """Restart SSH server on remote device"""
        service_name = self.get_ssh_service_name()
        
        console.print("[yellow]⚠️  Warning: Restarting SSH server will briefly disconnect this session![/yellow]")
        if not Confirm.ask("Are you sure you want to continue?"):
            return {"success": False, "message": "Operation cancelled by user"}
        
        try:
            if self.os_type == "Linux":
                result = self.execute_command(f"sudo systemctl restart {service_name}")
                
                if result["exit_code"] == 0:
                    console.print("[cyan]Waiting for server to restart...[/cyan]")
                    time.sleep(3)
                    
                    # Verify restart
                    status = self.check_ssh_status()
                    return {
                        "success": status["running"],
                        "message": "SSH server restarted successfully" if status["running"] else "Restart completed but status unclear",
                        "details": result["output"]
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to restart SSH server",
                        "details": result["error"]
                    }
                    
            elif self.os_type == "Darwin":
                # Stop and start
                self.execute_command("sudo systemsetup -setremotelogin off")
                time.sleep(2)
                result = self.execute_command("sudo systemsetup -setremotelogin on")
                
                return {
                    "success": result["exit_code"] == 0,
                    "message": "SSH server restarted successfully" if result["exit_code"] == 0 else "Failed to restart",
                    "details": result["output"]
                }
                
            elif self.os_type == "Windows":
                result = self.execute_command(f"powershell Restart-Service {service_name}")
                return {
                    "success": result["exit_code"] == 0,
                    "message": "SSH server restarted successfully" if result["exit_code"] == 0 else "Failed to restart",
                    "details": result["output"]
                }
                
            else:
                return {"success": False, "message": f"Unsupported OS: {self.os_type}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def enable_ssh_autostart(self):
        """Enable SSH server to start automatically on boot"""
        service_name = self.get_ssh_service_name()
        
        try:
            if self.os_type == "Linux":
                result = self.execute_command(f"sudo systemctl enable {service_name}")
                return {
                    "success": result["exit_code"] == 0,
                    "message": "SSH server enabled for autostart" if result["exit_code"] == 0 else "Failed to enable",
                    "details": result["output"]
                }
                
            elif self.os_type == "Windows":
                result = self.execute_command(f"powershell Set-Service -Name {service_name} -StartupType Automatic")
                return {
                    "success": result["exit_code"] == 0,
                    "message": "SSH server enabled for autostart" if result["exit_code"] == 0 else "Failed to enable",
                    "details": result["output"]
                }
                
            elif self.os_type == "Darwin":
                return {
                    "success": True,
                    "message": "SSH autostart is managed by systemsetup on macOS"
                }
                
            else:
                return {"success": False, "message": f"Unsupported OS: {self.os_type}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def disable_ssh_autostart(self):
        """Disable SSH server from starting automatically on boot"""
        service_name = self.get_ssh_service_name()
        
        try:
            if self.os_type == "Linux":
                result = self.execute_command(f"sudo systemctl disable {service_name}")
                return {
                    "success": result["exit_code"] == 0,
                    "message": "SSH server disabled from autostart" if result["exit_code"] == 0 else "Failed to disable",
                    "details": result["output"]
                }
                
            elif self.os_type == "Windows":
                result = self.execute_command(f"powershell Set-Service -Name {service_name} -StartupType Manual")
                return {
                    "success": result["exit_code"] == 0,
                    "message": "SSH server disabled from autostart" if result["exit_code"] == 0 else "Failed to disable",
                    "details": result["output"]
                }
                
            elif self.os_type == "Darwin":
                return {
                    "success": True,
                    "message": "SSH autostart is managed by systemsetup on macOS"
                }
                
            else:
                return {"success": False, "message": f"Unsupported OS: {self.os_type}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_ssh_config(self):
        """Get SSH server configuration"""
        try:
            if self.os_type in ["Linux", "Darwin"]:
                config_path = "/etc/ssh/sshd_config"
                result = self.execute_command(f"cat {config_path}")
                
                return {
                    "success": result["exit_code"] == 0,
                    "config": result["output"],
                    "path": config_path
                }
                
            elif self.os_type == "Windows":
                config_path = "C:\\ProgramData\\ssh\\sshd_config"
                result = self.execute_command(f"type {config_path}")
                
                return {
                    "success": result["exit_code"] == 0,
                    "config": result["output"],
                    "path": config_path
                }
                
            else:
                return {"success": False, "message": f"Unsupported OS: {self.os_type}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_ssh_logs(self, lines=50):
        """Get SSH server logs"""
        try:
            if self.os_type == "Linux":
                # Try journalctl first, then fallback to log files
                result = self.execute_command(f"sudo journalctl -u sshd -u ssh -n {lines} --no-pager")
                
                if result["exit_code"] != 0:
                    result = self.execute_command(f"sudo tail -n {lines} /var/log/auth.log /var/log/secure 2>/dev/null | grep sshd")
                
                return {
                    "success": result["exit_code"] == 0,
                    "logs": result["output"]
                }
                
            elif self.os_type == "Darwin":
                result = self.execute_command(f"sudo tail -n {lines} /var/log/system.log | grep sshd")
                return {
                    "success": result["exit_code"] == 0,
                    "logs": result["output"]
                }
                
            elif self.os_type == "Windows":
                result = self.execute_command(f"powershell Get-EventLog -LogName Security -Newest {lines} | Where-Object {{$_.Source -like '*ssh*'}} | Format-List")
                return {
                    "success": result["exit_code"] == 0,
                    "logs": result["output"]
                }
                
            else:
                return {"success": False, "message": f"Unsupported OS: {self.os_type}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def display_server_status(self):
        """Display comprehensive SSH server status"""
        console.clear()
        
        with console.status("[cyan]Checking SSH server status...[/cyan]"):
            status = self.check_ssh_status()
        
        # Create status table
        table = Table(title="SSH Server Status", show_header=True, header_style="bold magenta", border_style="cyan")
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="green")
        
        # Basic info
        table.add_row("Remote Host", self.device_info.get("host", "Unknown"))
        table.add_row("Operating System", self.os_type)
        table.add_row("Service Name", status["service_name"])
        
        # Running status
        running = status["running"]
        status_icon = "✓" if running else "✗"
        status_color = "green" if running else "red"
        table.add_row("Running", f"[{status_color}]{status_icon} {'YES' if running else 'NO'}[/{status_color}]")
        
        # Enabled status
        enabled = status["enabled"]
        enabled_icon = "✓" if enabled else "✗"
        enabled_color = "green" if enabled else "yellow"
        table.add_row("Autostart", f"[{enabled_color}]{enabled_icon} {'ENABLED' if enabled else 'DISABLED'}[/{enabled_color}]")
        
        # Timestamp
        table.add_row("Last Check", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        console.print(table)
        console.print()
        
        # Display detailed status
        if status.get("status_output"):
            console.print(Panel(
                status["status_output"][:500],  # Limit output
                title="Service Status Details",
                border_style="blue"
            ))
        
        # Display ports
        if status.get("ports"):
            console.print()
            console.print(Panel(
                status["ports"],
                title="Listening Ports",
                border_style="green"
            ))
        
        return status


def run(connection_manager=None):
    """Entry point for remote server actions"""
    server = RemoteServerActions(connection_manager)
    
    if not connection_manager or not connection_manager.ssh_client:
        console.print("[red]Error: No active SSH connection[/red]")
        console.print("[yellow]Please connect to a device first[/yellow]")
        console.input("\n[dim]Press Enter to continue...[/dim]")
        return
    
    # Use existing connection
    server.set_connection(
        connection_manager.ssh_client,
        connection_manager.current_device
    )
    
    while True:
        console.clear()
        console.print(Panel(
            f"[bold cyan]Remote Server Actions[/bold cyan]\n"
            f"Connected to: {server.device_info.get('host', 'Unknown')}\n"
            f"OS: {server.os_type}\n"
            f"Manage SSH/SSHD Server",
            border_style="cyan"
        ))
        
        console.print("\n[bold]Server Control:[/bold]")
        console.print("1. Check Server Status")
        console.print("2. Start SSH Server")
        console.print("3. Stop SSH Server")
        console.print("4. Restart SSH Server")
        console.print()
        console.print("[bold]Startup Configuration:[/bold]")
        console.print("5. Enable Autostart (Boot)")
        console.print("6. Disable Autostart")
        console.print()
        console.print("[bold]Advanced:[/bold]")
        console.print("7. View Configuration")
        console.print("8. View Server Logs")
        console.print("9. Full Status Report")
        console.print()
        console.print("0. Back")
        
        choice = console.input("\n[cyan]Select option:[/cyan] ").strip()
        
        if choice == "1":
            server.display_server_status()
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
        elif choice == "2":
            with console.status("[cyan]Starting SSH server...[/cyan]"):
                result = server.start_ssh_server()
            
            if result["success"]:
                console.print(f"\n[green]✓ {result['message']}[/green]")
            else:
                console.print(f"\n[red]✗ {result['message']}[/red]")
            
            if result.get("details"):
                console.print(f"\n[dim]{result['details'][:200]}[/dim]")
            
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
        elif choice == "3":
            result = server.stop_ssh_server()
            
            if result["success"]:
                console.print(f"\n[green]✓ {result['message']}[/green]")
            else:
                console.print(f"\n[yellow]{result['message']}[/yellow]")
            
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
        elif choice == "4":
            result = server.restart_ssh_server()
            
            if result["success"]:
                console.print(f"\n[green]✓ {result['message']}[/green]")
            else:
                console.print(f"\n[red]✗ {result['message']}[/red]")
            
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
        elif choice == "5":
            with console.status("[cyan]Enabling autostart...[/cyan]"):
                result = server.enable_ssh_autostart()
            
            if result["success"]:
                console.print(f"\n[green]✓ {result['message']}[/green]")
            else:
                console.print(f"\n[red]✗ {result['message']}[/red]")
            
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
        elif choice == "6":
            with console.status("[cyan]Disabling autostart...[/cyan]"):
                result = server.disable_ssh_autostart()
            
            if result["success"]:
                console.print(f"\n[green]✓ {result['message']}[/green]")
            else:
                console.print(f"\n[red]✗ {result['message']}[/red]")
            
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
        elif choice == "7":
            with console.status("[cyan]Loading configuration...[/cyan]"):
                result = server.get_ssh_config()
            
            if result["success"]:
                console.print(Panel(
                    result["config"],
                    title=f"SSH Configuration: {result['path']}",
                    border_style="blue"
                ))
            else:
                console.print(f"\n[red]✗ {result['message']}[/red]")
            
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
        elif choice == "8":
            lines = console.input("[cyan]Number of log lines (default 50):[/cyan] ").strip()
            lines = int(lines) if lines.isdigit() else 50
            
            with console.status("[cyan]Loading logs...[/cyan]"):
                result = server.get_ssh_logs(lines)
            
            if result["success"]:
                console.print(Panel(
                    result["logs"],
                    title=f"SSH Server Logs (Last {lines} lines)",
                    border_style="yellow"
                ))
            else:
                console.print(f"\n[red]✗ {result['message']}[/red]")
            
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
        elif choice == "9":
            status = server.display_server_status()
            
            console.print("\n[bold cyan]Additional Information:[/bold cyan]")
            
            # Get configuration
            with console.status("[cyan]Loading configuration...[/cyan]"):
                config = server.get_ssh_config()
            
            if config["success"]:
                console.print(f"\n[green]✓ Configuration accessible at: {config['path']}[/green]")
            
            # Get logs
            with console.status("[cyan]Loading recent logs...[/cyan]"):
                logs = server.get_ssh_logs(10)
            
            if logs["success"] and logs["logs"]:
                console.print("\n[bold]Recent Log Entries:[/bold]")
                console.print(Panel(logs["logs"][:500], border_style="yellow"))
            
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
        elif choice == "0":
            break


if __name__ == "__main__":
    run()
