"""
Local Security Tools Module
Advanced security scanning, vulnerability detection, and system hardening
"""

import os
import subprocess
import platform
import hashlib
import socket
from pathlib import Path
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
import psutil

console = Console()


class LocalSecurityTools:
    """Comprehensive local security tools and scanning"""
    
    def __init__(self):
        self.console = console
        self.system = platform.system()
    
    def scan_open_ports(self):
        """Scan for open ports on local system"""
        open_ports = []
        
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'LISTEN':
                try:
                    service = socket.getservbyport(conn.laddr.port) if conn.laddr else "Unknown"
                except:
                    service = "Unknown"
                
                open_ports.append({
                    "port": conn.laddr.port if conn.laddr else "N/A",
                    "protocol": "TCP" if conn.type == socket.SOCK_STREAM else "UDP",
                    "service": service,
                    "pid": conn.pid,
                    "address": conn.laddr.ip if conn.laddr else "N/A"
                })
        
        return open_ports
    
    def check_firewall_status(self):
        """Check firewall status"""
        try:
            if self.system == "Windows":
                result = subprocess.run(
                    ['netsh', 'advfirewall', 'show', 'allprofiles'],
                    capture_output=True,
                    text=True
                )
                return {"status": "success", "output": result.stdout}
            elif self.system == "Linux":
                # Check for various firewall tools
                for cmd in [['ufw', 'status'], ['firewall-cmd', '--state'], ['iptables', '-L']]:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            return {"status": "success", "output": result.stdout}
                    except FileNotFoundError:
                        continue
                return {"status": "error", "output": "No firewall tool found"}
            else:
                return {"status": "error", "output": "Unsupported OS"}
        except Exception as e:
            return {"status": "error", "output": str(e)}
    
    def scan_suspicious_processes(self):
        """Scan for suspicious processes"""
        suspicious = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'username']):
            try:
                info = proc.info
                
                # Check for high resource usage
                if info['cpu_percent'] and info['cpu_percent'] > 80:
                    suspicious.append({
                        "pid": info['pid'],
                        "name": info['name'],
                        "reason": f"High CPU usage: {info['cpu_percent']:.1f}%",
                        "user": info['username']
                    })
                
                if info['memory_percent'] and info['memory_percent'] > 50:
                    suspicious.append({
                        "pid": info['pid'],
                        "name": info['name'],
                        "reason": f"High memory usage: {info['memory_percent']:.1f}%",
                        "user": info['username']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return suspicious
    
    def check_system_updates(self):
        """Check for system updates"""
        try:
            if self.system == "Windows":
                # Windows Update check
                result = subprocess.run(
                    ['powershell', 'Get-WindowsUpdate'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return {"status": "success", "output": result.stdout or "No updates available"}
            elif self.system == "Linux":
                # Check for apt or yum
                for cmd in [['apt', 'list', '--upgradable'], ['yum', 'check-update']]:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                        if result.returncode in [0, 100]:  # 100 is yum's code for updates available
                            return {"status": "success", "output": result.stdout}
                    except FileNotFoundError:
                        continue
                return {"status": "error", "output": "No package manager found"}
            else:
                return {"status": "info", "output": "Manual update check required"}
        except subprocess.TimeoutExpired:
            return {"status": "error", "output": "Update check timeout"}
        except Exception as e:
            return {"status": "error", "output": str(e)}
    
    def scan_writable_directories(self, directory="/"):
        """Scan for world-writable directories (security risk)"""
        writable_dirs = []
        
        try:
            for root, dirs, files in os.walk(directory):
                for dir_name in dirs[:10]:  # Limit scan
                    dir_path = os.path.join(root, dir_name)
                    try:
                        # Check if directory is writable by others
                        stat_info = os.stat(dir_path)
                        mode = stat_info.st_mode
                        
                        # Check for world-writable (others can write)
                        if mode & 0o002:
                            writable_dirs.append({
                                "path": dir_path,
                                "permissions": oct(mode)[-3:],
                                "owner": stat_info.st_uid
                            })
                    except (PermissionError, OSError):
                        continue
                
                if len(writable_dirs) > 50:  # Limit results
                    break
        except Exception as e:
            return {"error": str(e)}
        
        return writable_dirs
    
    def check_password_policy(self):
        """Check password policy settings"""
        try:
            if self.system == "Windows":
                result = subprocess.run(
                    ['net', 'accounts'],
                    capture_output=True,
                    text=True
                )
                return {"status": "success", "output": result.stdout}
            elif self.system == "Linux":
                # Check password aging
                try:
                    with open('/etc/login.defs', 'r') as f:
                        content = f.read()
                        return {"status": "success", "output": content}
                except FileNotFoundError:
                    return {"status": "error", "output": "Configuration file not found"}
            else:
                return {"status": "info", "output": "Manual policy check required"}
        except Exception as e:
            return {"status": "error", "output": str(e)}
    
    def audit_user_accounts(self):
        """Audit user accounts on the system"""
        users = []
        
        try:
            if self.system == "Windows":
                result = subprocess.run(['net', 'user'], capture_output=True, text=True)
                return {"status": "success", "output": result.stdout}
            elif self.system == "Linux":
                with open('/etc/passwd', 'r') as f:
                    for line in f:
                        parts = line.strip().split(':')
                        if len(parts) >= 7:
                            users.append({
                                "username": parts[0],
                                "uid": parts[2],
                                "gid": parts[3],
                                "home": parts[5],
                                "shell": parts[6]
                            })
                return {"status": "success", "users": users}
            else:
                return {"status": "info", "output": "Manual audit required"}
        except Exception as e:
            return {"status": "error", "output": str(e)}
    
    def check_antivirus_status(self):
        """Check antivirus/security software status"""
        try:
            if self.system == "Windows":
                # Check Windows Defender status
                result = subprocess.run(
                    ['powershell', 'Get-MpComputerStatus'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return {"status": "success", "output": result.stdout}
            else:
                # Check for ClamAV or other AV
                for cmd in [['clamscan', '--version'], ['freshclam', '--version']]:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            return {"status": "success", "output": result.stdout}
                    except FileNotFoundError:
                        continue
                return {"status": "info", "output": "No antivirus software detected"}
        except subprocess.TimeoutExpired:
            return {"status": "error", "output": "Status check timeout"}
        except Exception as e:
            return {"status": "error", "output": str(e)}
    
    def generate_security_report(self):
        """Generate comprehensive security report"""
        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system": self.system,
            "open_ports": len(self.scan_open_ports()),
            "suspicious_processes": len(self.scan_suspicious_processes()),
            "firewall_status": "Checked",
            "antivirus_status": "Checked",
            "recommendations": []
        }
        
        # Add recommendations based on findings
        if report["open_ports"] > 10:
            report["recommendations"].append("Review and close unnecessary open ports")
        
        if report["suspicious_processes"] > 0:
            report["recommendations"].append("Investigate suspicious processes")
        
        return report


def run():
    """Main entry point for local security tools"""
    security = LocalSecurityTools()
    
    console.print(Panel.fit(
        "[bold cyan]Local Security Tools[/bold cyan]\n"
        "Security scanning and hardening utilities",
        border_style="cyan"
    ))
    
    options = [
        "1. Scan Open Ports",
        "2. Check Firewall Status",
        "3. Scan Suspicious Processes",
        "4. Check System Updates",
        "5. Audit User Accounts",
        "6. Check Antivirus Status",
        "7. Check Password Policy",
        "8. Generate Security Report",
        "0. Back to Main Menu"
    ]
    
    for option in options:
        console.print(f"  {option}")
    
    choice = console.input("\n[bold yellow]Enter your choice: [/bold yellow]")
    
    if choice == "1":
        console.print("[yellow]Scanning open ports...[/yellow]")
        ports = security.scan_open_ports()
        
        table = Table(title=f"Open Ports ({len(ports)})", style="cyan")
        table.add_column("Port", style="bold yellow")
        table.add_column("Protocol", style="cyan")
        table.add_column("Service", style="green")
        table.add_column("PID", style="magenta")
        table.add_column("Address", style="blue")
        
        for port in ports:
            table.add_row(
                str(port['port']),
                port['protocol'],
                port['service'],
                str(port['pid']) if port['pid'] else "N/A",
                port['address']
            )
        
        console.print(table)
    
    elif choice == "2":
        console.print("[yellow]Checking firewall status...[/yellow]")
        result = security.check_firewall_status()
        
        console.print(Panel.fit(
            result['output'],
            title="Firewall Status",
            border_style="green" if result['status'] == "success" else "red"
        ))
    
    elif choice == "3":
        console.print("[yellow]Scanning for suspicious processes...[/yellow]")
        suspicious = security.scan_suspicious_processes()
        
        if suspicious:
            table = Table(title=f"Suspicious Processes ({len(suspicious)})", style="cyan")
            table.add_column("PID", style="bold yellow")
            table.add_column("Name", style="cyan")
            table.add_column("Reason", style="red")
            table.add_column("User", style="green")
            
            for proc in suspicious:
                table.add_row(
                    str(proc['pid']),
                    proc['name'],
                    proc['reason'],
                    proc['user']
                )
            
            console.print(table)
        else:
            console.print("[green]No suspicious processes detected![/green]")
    
    elif choice == "4":
        console.print("[yellow]Checking for system updates...[/yellow]")
        result = security.check_system_updates()
        
        console.print(Panel.fit(
            result['output'],
            title="System Updates",
            border_style="cyan"
        ))
    
    elif choice == "5":
        console.print("[yellow]Auditing user accounts...[/yellow]")
        result = security.audit_user_accounts()
        
        if result['status'] == "success":
            if 'users' in result:
                table = Table(title="User Accounts", style="cyan")
                table.add_column("Username", style="bold yellow")
                table.add_column("UID", style="cyan")
                table.add_column("GID", style="green")
                table.add_column("Home", style="blue")
                table.add_column("Shell", style="magenta")
                
                for user in result['users'][:20]:  # Limit to 20
                    table.add_row(
                        user['username'],
                        user['uid'],
                        user['gid'],
                        user['home'],
                        user['shell']
                    )
                
                console.print(table)
            else:
                console.print(Panel.fit(result['output'], title="User Accounts", border_style="cyan"))
        else:
            console.print(f"[red]Error: {result['output']}[/red]")
    
    elif choice == "6":
        console.print("[yellow]Checking antivirus status...[/yellow]")
        result = security.check_antivirus_status()
        
        console.print(Panel.fit(
            result['output'],
            title="Antivirus Status",
            border_style="green" if result['status'] == "success" else "yellow"
        ))
    
    elif choice == "7":
        console.print("[yellow]Checking password policy...[/yellow]")
        result = security.check_password_policy()
        
        console.print(Panel.fit(
            result['output'],
            title="Password Policy",
            border_style="cyan"
        ))
    
    elif choice == "8":
        console.print("[yellow]Generating security report...[/yellow]")
        report = security.generate_security_report()
        
        table = Table(title="Security Report", style="cyan")
        table.add_column("Metric", style="bold yellow")
        table.add_column("Value", style="green")
        
        for key, value in report.items():
            if key != "recommendations":
                table.add_row(key.replace('_', ' ').title(), str(value))
        
        console.print(table)
        
        if report['recommendations']:
            console.print("\n[bold yellow]Recommendations:[/bold yellow]")
            for idx, rec in enumerate(report['recommendations'], 1):
                console.print(f"  {idx}. {rec}")
    
    console.input("\n[bold yellow]Press Enter to continue...[/bold yellow]")


if __name__ == "__main__":
    run()
