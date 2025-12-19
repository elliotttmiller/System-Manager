"""
Local Network Tools Module
Advanced network diagnostics, monitoring, and analysis tools
"""

import socket
import subprocess
import platform
import psutil
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
import json

console = Console()


class LocalNetworkTools:
    """Comprehensive local network diagnostics and tools"""
    
    def __init__(self):
        self.console = console
        self.system = platform.system()
    
    def get_network_interfaces(self):
        """Get all network interfaces and their details"""
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        interface_info = []
        
        for interface_name, addresses in interfaces.items():
            interface_data = {
                "name": interface_name,
                "addresses": [],
                "is_up": stats[interface_name].isup if interface_name in stats else False,
                "speed": f"{stats[interface_name].speed} Mbps" if interface_name in stats else "Unknown"
            }
            
            for addr in addresses:
                if addr.family == socket.AF_INET:
                    interface_data["addresses"].append({
                        "type": "IPv4",
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    })
                elif addr.family == socket.AF_INET6:
                    interface_data["addresses"].append({
                        "type": "IPv6",
                        "address": addr.address,
                        "netmask": addr.netmask
                    })
            
            interface_info.append(interface_data)
        
        return interface_info
    
    def get_active_connections(self):
        """Get all active network connections"""
        connections = []
        
        for conn in psutil.net_connections(kind='inet'):
            try:
                connections.append({
                    "protocol": "TCP" if conn.type == socket.SOCK_STREAM else "UDP",
                    "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                    "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                    "status": conn.status,
                    "pid": conn.pid
                })
            except Exception:
                continue
        
        return connections
    
    def get_routing_table(self):
        """Get system routing table"""
        try:
            if self.system == "Windows":
                result = subprocess.run(['route', 'print'], capture_output=True, text=True)
            else:
                result = subprocess.run(['route', '-n'], capture_output=True, text=True)
            
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"
    
    def ping_host(self, host, count=4):
        """Ping a host and return results"""
        param = '-n' if self.system == "Windows" else '-c'
        
        try:
            result = subprocess.run(
                ['ping', param, str(count), host],
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "host": host,
                "output": result.stdout,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "host": host,
                "output": "Ping timeout",
                "success": False
            }
        except Exception as e:
            return {
                "host": host,
                "output": str(e),
                "success": False
            }
    
    def traceroute(self, host):
        """Perform traceroute to host"""
        command = 'tracert' if self.system == "Windows" else 'traceroute'
        
        try:
            result = subprocess.run(
                [command, host],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            return "Traceroute timeout"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def dns_lookup(self, hostname):
        """Perform DNS lookup"""
        try:
            ip_address = socket.gethostbyname(hostname)
            
            # Get all addresses
            _, _, addresses = socket.gethostbyname_ex(hostname)
            
            return {
                "hostname": hostname,
                "primary_ip": ip_address,
                "all_ips": addresses,
                "success": True
            }
        except socket.gaierror as e:
            return {
                "hostname": hostname,
                "error": str(e),
                "success": False
            }
    
    def reverse_dns_lookup(self, ip_address):
        """Perform reverse DNS lookup"""
        try:
            hostname = socket.gethostbyaddr(ip_address)
            return {
                "ip": ip_address,
                "hostname": hostname[0],
                "aliases": hostname[1],
                "success": True
            }
        except socket.herror as e:
            return {
                "ip": ip_address,
                "error": str(e),
                "success": False
            }
    
    def port_scan(self, host, ports):
        """Scan specific ports on a host"""
        results = []
        
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            
            try:
                result = sock.connect_ex((host, port))
                status = "Open" if result == 0 else "Closed"
                
                # Try to get service name
                try:
                    service = socket.getservbyport(port)
                except:
                    service = "Unknown"
                
                results.append({
                    "port": port,
                    "status": status,
                    "service": service
                })
            except socket.error:
                results.append({
                    "port": port,
                    "status": "Error",
                    "service": "Unknown"
                })
            finally:
                sock.close()
        
        return results
    
    def get_network_bandwidth(self):
        """Get current network bandwidth usage"""
        net_io_before = psutil.net_io_counters()
        
        import time
        time.sleep(1)
        
        net_io_after = psutil.net_io_counters()
        
        bytes_sent = net_io_after.bytes_sent - net_io_before.bytes_sent
        bytes_recv = net_io_after.bytes_recv - net_io_before.bytes_recv
        
        return {
            "upload_speed": f"{bytes_sent / 1024:.2f} KB/s",
            "download_speed": f"{bytes_recv / 1024:.2f} KB/s",
            "upload_speed_mbps": f"{bytes_sent * 8 / (1024 * 1024):.2f} Mbps",
            "download_speed_mbps": f"{bytes_recv * 8 / (1024 * 1024):.2f} Mbps"
        }
    
    def get_public_ip(self):
        """Get public IP address"""
        try:
            # Try multiple services
            import urllib.request
            
            services = [
                'https://api.ipify.org',
                'https://ifconfig.me/ip',
                'https://icanhazip.com'
            ]
            
            for service in services:
                try:
                    response = urllib.request.urlopen(service, timeout=5)
                    return response.read().decode('utf-8').strip()
                except:
                    continue
            
            return "Unable to determine"
        except Exception as e:
            return f"Error: {str(e)}"


def run():
    """Main entry point for local network tools"""
    tools = LocalNetworkTools()
    
    console.print(Panel.fit(
        "[bold cyan]Local Network Tools[/bold cyan]\n"
        "Advanced network diagnostics and monitoring",
        border_style="cyan"
    ))
    
    options = [
        "1. Show Network Interfaces",
        "2. Show Active Connections",
        "3. Ping Host",
        "4. DNS Lookup",
        "5. Reverse DNS Lookup",
        "6. Traceroute",
        "7. Port Scan",
        "8. Network Bandwidth",
        "9. Show Routing Table",
        "10. Get Public IP",
        "0. Back to Main Menu"
    ]
    
    for option in options:
        console.print(f"  {option}")
    
    choice = console.input("\n[bold yellow]Enter your choice: [/bold yellow]")
    
    if choice == "1":
        interfaces = tools.get_network_interfaces()
        
        for interface in interfaces:
            table = Table(title=f"Interface: {interface['name']}", style="cyan")
            table.add_column("Property", style="bold yellow")
            table.add_column("Value", style="green")
            
            table.add_row("Status", "Up" if interface['is_up'] else "Down")
            table.add_row("Speed", interface['speed'])
            
            for addr in interface['addresses']:
                table.add_row(f"{addr['type']} Address", addr['address'])
                if 'netmask' in addr:
                    table.add_row(f"{addr['type']} Netmask", addr['netmask'])
            
            console.print(table)
            console.print()
    
    elif choice == "2":
        connections = tools.get_active_connections()
        
        table = Table(title=f"Active Connections ({len(connections)})", style="cyan")
        table.add_column("Protocol", style="bold yellow")
        table.add_column("Local Address", style="cyan")
        table.add_column("Remote Address", style="green")
        table.add_column("Status", style="magenta")
        table.add_column("PID", style="blue")
        
        for conn in connections[:50]:  # Limit to 50
            table.add_row(
                conn['protocol'],
                conn['local_address'],
                conn['remote_address'],
                conn['status'],
                str(conn['pid']) if conn['pid'] else "N/A"
            )
        
        console.print(table)
        if len(connections) > 50:
            console.print(f"[yellow]Showing first 50 of {len(connections)} connections[/yellow]")
    
    elif choice == "3":
        host = console.input("[bold cyan]Enter host to ping: [/bold cyan]")
        count = console.input("[bold cyan]Enter number of pings (default 4): [/bold cyan]") or "4"
        
        console.print(f"[yellow]Pinging {host}...[/yellow]")
        result = tools.ping_host(host, int(count))
        
        console.print(Panel.fit(
            result['output'],
            title=f"Ping Results: {host}",
            border_style="green" if result['success'] else "red"
        ))
    
    elif choice == "4":
        hostname = console.input("[bold cyan]Enter hostname: [/bold cyan]")
        result = tools.dns_lookup(hostname)
        
        if result['success']:
            table = Table(title=f"DNS Lookup: {hostname}", style="cyan")
            table.add_column("Property", style="bold yellow")
            table.add_column("Value", style="green")
            
            table.add_row("Primary IP", result['primary_ip'])
            table.add_row("All IPs", ", ".join(result['all_ips']))
            
            console.print(table)
        else:
            console.print(f"[red]Error: {result['error']}[/red]")
    
    elif choice == "5":
        ip = console.input("[bold cyan]Enter IP address: [/bold cyan]")
        result = tools.reverse_dns_lookup(ip)
        
        if result['success']:
            table = Table(title=f"Reverse DNS Lookup: {ip}", style="cyan")
            table.add_column("Property", style="bold yellow")
            table.add_column("Value", style="green")
            
            table.add_row("Hostname", result['hostname'])
            if result['aliases']:
                table.add_row("Aliases", ", ".join(result['aliases']))
            
            console.print(table)
        else:
            console.print(f"[red]Error: {result['error']}[/red]")
    
    elif choice == "6":
        host = console.input("[bold cyan]Enter host for traceroute: [/bold cyan]")
        console.print(f"[yellow]Performing traceroute to {host}... This may take a while.[/yellow]")
        result = tools.traceroute(host)
        
        console.print(Panel.fit(
            result,
            title=f"Traceroute: {host}",
            border_style="cyan"
        ))
    
    elif choice == "7":
        host = console.input("[bold cyan]Enter host to scan: [/bold cyan]")
        ports_input = console.input("[bold cyan]Enter ports to scan (comma-separated, e.g., 22,80,443): [/bold cyan]")
        ports = [int(p.strip()) for p in ports_input.split(',')]
        
        console.print(f"[yellow]Scanning ports on {host}...[/yellow]")
        results = tools.port_scan(host, ports)
        
        table = Table(title=f"Port Scan Results: {host}", style="cyan")
        table.add_column("Port", style="bold yellow")
        table.add_column("Status", style="green")
        table.add_column("Service", style="cyan")
        
        for result in results:
            status_color = "green" if result['status'] == "Open" else "red"
            table.add_row(
                str(result['port']),
                f"[{status_color}]{result['status']}[/{status_color}]",
                result['service']
            )
        
        console.print(table)
    
    elif choice == "8":
        console.print("[yellow]Measuring bandwidth...[/yellow]")
        bandwidth = tools.get_network_bandwidth()
        
        table = Table(title="Network Bandwidth", style="cyan")
        table.add_column("Metric", style="bold yellow")
        table.add_column("Value", style="green")
        
        for key, value in bandwidth.items():
            table.add_row(key.replace('_', ' ').title(), value)
        
        console.print(table)
    
    elif choice == "9":
        console.print("[yellow]Fetching routing table...[/yellow]")
        routing_table = tools.get_routing_table()
        
        console.print(Panel.fit(
            routing_table,
            title="Routing Table",
            border_style="cyan"
        ))
    
    elif choice == "10":
        console.print("[yellow]Fetching public IP...[/yellow]")
        public_ip = tools.get_public_ip()
        
        console.print(Panel.fit(
            f"[bold green]Public IP: {public_ip}[/bold green]",
            border_style="cyan"
        ))
    
    console.input("\n[bold yellow]Press Enter to continue...[/bold yellow]")


if __name__ == "__main__":
    run()
