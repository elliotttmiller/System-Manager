"""
Local Service Monitor
Monitors and manages services on the local laptop
Ensures SSH server is running and accessible for remote connections
"""

import subprocess
import socket
import os
import time
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import platform

console = Console()


class LocalServiceMonitor:
    """Monitor and manage local services including SSH server"""
    
    def __init__(self, config_path="config/service_monitor.json"):
        self.console = console
        self.config_path = config_path
        self.config = self.load_config()
        self.system = platform.system()
        
    def load_config(self):
        """Load service monitor configuration"""
        default_config = {
            "ssh_port": 22,
            "check_interval": 60,
            "auto_start": True,
            "services": {
                "ssh": {"enabled": True, "port": 22},
                "http": {"enabled": False, "port": 80},
                "https": {"enabled": False, "port": 443}
            },
            "notifications": True,
            "log_file": "logs/service_monitor.log"
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return {**default_config, **json.load(f)}
            else:
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load config: {e}[/yellow]")
            return default_config
    
    def save_config(self):
        """Save current configuration"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            console.print(f"[red]Error saving config: {e}[/red]")
            return False
    
    def check_port_open(self, port, host="localhost", timeout=3):
        """Check if a port is open and listening"""
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False
    
    def check_ssh_server_status(self):
        """Check if SSH server is running"""
        port = self.config["ssh_port"]
        
        # Check if port is listening
        port_open = self.check_port_open(port)
        
        # Get service status based on OS
        service_status = self.get_service_status("ssh")
        
        return {
            "running": port_open and service_status["running"],
            "port_open": port_open,
            "service_status": service_status,
            "port": port,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_service_status(self, service_name):
        """Get service status based on operating system"""
        try:
            if self.system == "Windows":
                # Check OpenSSH Server on Windows
                result = subprocess.run(
                    ["powershell", "-Command", f"Get-Service -Name sshd | Select-Object -Property Status"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                running = "Running" in result.stdout
                return {"running": running, "output": result.stdout.strip()}
                
            elif self.system == "Linux":
                # Check SSH service on Linux
                result = subprocess.run(
                    ["systemctl", "is-active", "ssh"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                running = result.stdout.strip() == "active"
                return {"running": running, "output": result.stdout.strip()}
                
            elif self.system == "Darwin":  # macOS
                # Check SSH on macOS
                result = subprocess.run(
                    ["launchctl", "list", "com.openssh.sshd"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                running = result.returncode == 0
                return {"running": running, "output": result.stdout.strip()}
                
            else:
                return {"running": False, "output": "Unsupported OS"}
                
        except Exception as e:
            return {"running": False, "output": f"Error: {str(e)}"}
    
    def start_ssh_server(self):
        """Start SSH server based on operating system"""
        try:
            if self.system == "Windows":
                # Start OpenSSH Server on Windows
                result = subprocess.run(
                    ["powershell", "-Command", "Start-Service sshd"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                success = result.returncode == 0
                
                if success:
                    # Set to start automatically
                    subprocess.run(
                        ["powershell", "-Command", "Set-Service -Name sshd -StartupType 'Automatic'"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                
                return {
                    "success": success,
                    "message": "SSH server started successfully" if success else result.stderr
                }
                
            elif self.system == "Linux":
                # Start SSH service on Linux
                result = subprocess.run(
                    ["sudo", "systemctl", "start", "ssh"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                success = result.returncode == 0
                
                if success:
                    # Enable to start on boot
                    subprocess.run(
                        ["sudo", "systemctl", "enable", "ssh"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                
                return {
                    "success": success,
                    "message": "SSH server started successfully" if success else result.stderr
                }
                
            elif self.system == "Darwin":  # macOS
                # Start SSH on macOS
                result = subprocess.run(
                    ["sudo", "systemsetup", "-setremotelogin", "on"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                success = result.returncode == 0
                
                return {
                    "success": success,
                    "message": "SSH server started successfully" if success else result.stderr
                }
                
            else:
                return {"success": False, "message": "Unsupported operating system"}
                
        except Exception as e:
            return {"success": False, "message": f"Error starting SSH server: {str(e)}"}
    
    def stop_ssh_server(self):
        """Stop SSH server"""
        try:
            if self.system == "Windows":
                result = subprocess.run(
                    ["powershell", "-Command", "Stop-Service sshd"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                success = result.returncode == 0
                
            elif self.system == "Linux":
                result = subprocess.run(
                    ["sudo", "systemctl", "stop", "ssh"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                success = result.returncode == 0
                
            elif self.system == "Darwin":
                result = subprocess.run(
                    ["sudo", "systemsetup", "-setremotelogin", "off"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                success = result.returncode == 0
                
            else:
                return {"success": False, "message": "Unsupported OS"}
            
            return {
                "success": success,
                "message": "SSH server stopped" if success else "Failed to stop"
            }
            
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def check_ssh_config(self):
        """Check SSH server configuration"""
        config_paths = {
            "Windows": "C:\\ProgramData\\ssh\\sshd_config",
            "Linux": "/etc/ssh/sshd_config",
            "Darwin": "/etc/ssh/sshd_config"
        }
        
        config_path = config_paths.get(self.system)
        
        if not config_path or not os.path.exists(config_path):
            return {
                "valid": False,
                "path": config_path,
                "message": "SSH config file not found"
            }
        
        try:
            with open(config_path, 'r') as f:
                config_content = f.read()
            
            # Basic validation
            checks = {
                "Port directive": "Port " in config_content or "#Port " in config_content,
                "PasswordAuthentication": "PasswordAuthentication" in config_content,
                "PubkeyAuthentication": "PubkeyAuthentication" in config_content
            }
            
            return {
                "valid": all(checks.values()),
                "path": config_path,
                "checks": checks,
                "message": "Configuration valid" if all(checks.values()) else "Configuration incomplete"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "path": config_path,
                "message": f"Error reading config: {str(e)}"
            }
    
    def get_network_info(self):
        """Get local network information for remote access"""
        try:
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Get hostname
            hostname = socket.gethostname()
            
            return {
                "hostname": hostname,
                "local_ip": local_ip,
                "ssh_port": self.config["ssh_port"],
                "connection_string": f"ssh {os.getlogin()}@{local_ip}"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "message": "Could not retrieve network information"
            }
    
    def display_status(self):
        """Display comprehensive service status"""
        console.clear()
        
        # Get all status information
        ssh_status = self.check_ssh_server_status()
        config_status = self.check_ssh_config()
        network_info = self.get_network_info()
        
        # Create status table
        table = Table(title="Local Service Monitor Status", show_header=True, header_style="bold magenta")
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")
        
        # SSH Server Status
        ssh_running = ssh_status["running"]
        status_icon = "✓" if ssh_running else "✗"
        status_color = "green" if ssh_running else "red"
        
        table.add_row(
            "SSH Server",
            f"[{status_color}]{status_icon} {'Running' if ssh_running else 'Stopped'}[/{status_color}]",
            f"Port {ssh_status['port']}"
        )
        
        # Port Status
        port_icon = "✓" if ssh_status["port_open"] else "✗"
        port_color = "green" if ssh_status["port_open"] else "red"
        
        table.add_row(
            "Port Listening",
            f"[{port_color}]{port_icon} {'Open' if ssh_status['port_open'] else 'Closed'}[/{port_color}]",
            f"Port {ssh_status['port']}"
        )
        
        # Configuration Status
        config_icon = "✓" if config_status["valid"] else "✗"
        config_color = "green" if config_status["valid"] else "yellow"
        
        table.add_row(
            "Configuration",
            f"[{config_color}]{config_icon} {config_status['message']}[/{config_color}]",
            config_status.get("path", "N/A")
        )
        
        console.print(table)
        console.print()
        
        # Network Information Panel
        if "error" not in network_info:
            network_panel = Panel(
                f"[cyan]Hostname:[/cyan] {network_info['hostname']}\n"
                f"[cyan]Local IP:[/cyan] {network_info['local_ip']}\n"
                f"[cyan]SSH Port:[/cyan] {network_info['ssh_port']}\n"
                f"[green]Connection:[/green] {network_info['connection_string']}",
                title="Network Information",
                border_style="green"
            )
            console.print(network_panel)
        
        return {
            "ssh_status": ssh_status,
            "config_status": config_status,
            "network_info": network_info
        }
    
    def auto_monitor(self, interval=None):
        """Continuously monitor and auto-start services"""
        if interval is None:
            interval = self.config["check_interval"]
        
        console.print(Panel(
            f"[green]Service Monitor Started[/green]\n"
            f"Check Interval: {interval} seconds\n"
            f"Auto-start: {'Enabled' if self.config['auto_start'] else 'Disabled'}\n"
            f"Press Ctrl+C to stop",
            title="Auto Monitor",
            border_style="blue"
        ))
        
        try:
            while True:
                status = self.display_status()
                
                # Auto-start SSH if enabled and not running
                if self.config["auto_start"] and not status["ssh_status"]["running"]:
                    console.print("\n[yellow]SSH server not running. Attempting to start...[/yellow]")
                    result = self.start_ssh_server()
                    
                    if result["success"]:
                        console.print(f"[green]✓ {result['message']}[/green]")
                    else:
                        console.print(f"[red]✗ {result['message']}[/red]")
                
                # Wait before next check
                console.print(f"\n[dim]Next check in {interval} seconds...[/dim]")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Service monitor stopped by user[/yellow]")


def run():
    """Entry point for the service monitor"""
    monitor = LocalServiceMonitor()
    
    while True:
        console.clear()
        console.print(Panel(
            "[bold cyan]Local Service Monitor[/bold cyan]\n"
            "Manage SSH Server and System Services",
            border_style="cyan"
        ))
        
        console.print("\n[bold]Options:[/bold]")
        console.print("1. Check Status")
        console.print("2. Start SSH Server")
        console.print("3. Stop SSH Server")
        console.print("4. Check Configuration")
        console.print("5. Auto Monitor (Continuous)")
        console.print("6. Settings")
        console.print("0. Back")
        
        choice = console.input("\n[cyan]Select option:[/cyan] ").strip()
        
        if choice == "1":
            monitor.display_status()
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
        elif choice == "2":
            result = monitor.start_ssh_server()
            if result["success"]:
                console.print(f"\n[green]✓ {result['message']}[/green]")
            else:
                console.print(f"\n[red]✗ {result['message']}[/red]")
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
        elif choice == "3":
            result = monitor.stop_ssh_server()
            if result["success"]:
                console.print(f"\n[green]✓ {result['message']}[/green]")
            else:
                console.print(f"\n[red]✗ {result['message']}[/red]")
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
        elif choice == "4":
            config_status = monitor.check_ssh_config()
            console.print(f"\n[cyan]Configuration Status:[/cyan]")
            console.print(f"Path: {config_status['path']}")
            console.print(f"Valid: {config_status['valid']}")
            console.print(f"Message: {config_status['message']}")
            if "checks" in config_status:
                console.print("\n[cyan]Checks:[/cyan]")
                for check, passed in config_status["checks"].items():
                    icon = "✓" if passed else "✗"
                    color = "green" if passed else "red"
                    console.print(f"  [{color}]{icon}[/{color}] {check}")
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
        elif choice == "5":
            monitor.auto_monitor()
            
        elif choice == "6":
            console.print("\n[bold]Current Settings:[/bold]")
            console.print(f"SSH Port: {monitor.config['ssh_port']}")
            console.print(f"Check Interval: {monitor.config['check_interval']} seconds")
            console.print(f"Auto-start: {monitor.config['auto_start']}")
            
            console.print("\n[yellow]Settings can be modified in:[/yellow]")
            console.print(f"{monitor.config_path}")
            console.input("\n[dim]Press Enter to continue...[/dim]")
            
        elif choice == "0":
            break


if __name__ == "__main__":
    run()
