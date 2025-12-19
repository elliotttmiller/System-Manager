"""
Remote Network Tools Module
Network diagnostics and monitoring on remote devices via SSH
"""

import paramiko
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
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


class RemoteNetworkTools:
    """Comprehensive remote network diagnostics via SSH"""
    
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
    
    def get_network_interfaces(self):
        """Get network interface information"""
        cmd = "ip addr show || ifconfig"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to get network interfaces')}
    
    def ping_host(self, target, count=4):
        """Ping a host"""
        cmd = f"ping -c {count} {target}"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Ping failed')}
    
    def traceroute(self, target):
        """Traceroute to a host"""
        cmd = f"traceroute {target} || tracepath {target}"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Traceroute failed')}
    
    def get_routing_table(self):
        """Get routing table"""
        cmd = "ip route || route -n"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to get routing table')}
    
    def get_listening_ports(self):
        """Get listening ports"""
        cmd = "ss -tulpn || netstat -tulpn"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to get listening ports')}
    
    def get_active_connections(self):
        """Get active network connections"""
        cmd = "ss -tupn || netstat -tupn"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to get active connections')}
    
    def dns_lookup(self, domain):
        """Perform DNS lookup"""
        cmd = f"nslookup {domain} || dig {domain}"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'DNS lookup failed')}
    
    def get_network_stats(self):
        """Get network statistics"""
        cmd = "ip -s link || ifconfig"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to get network stats')}
    
    def test_port(self, host, port):
        """Test if a port is open"""
        cmd = f"nc -zv {host} {port} 2>&1 || telnet {host} {port} 2>&1 | head -n 3"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Port test failed')}
    
    def get_firewall_rules(self):
        """Get firewall rules"""
        cmd = "sudo iptables -L -n -v || sudo ufw status verbose"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to get firewall rules')}
    
    def get_bandwidth_usage(self):
        """Get bandwidth usage"""
        cmd = "vnstat -d || iftop -t -s 5"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            # Fallback
            cmd = "cat /proc/net/dev"
            result = self.execute_command(cmd)
            return {"output": result['output']} if result['status'] == "success" else {"error": "Bandwidth monitoring not available"}
    
    def disconnect(self):
        """Close SSH connection"""
        if self.ssh_client:
            self.ssh_client.close()
            return {"status": "success", "message": "Disconnected"}
        return {"status": "error", "message": "Not connected"}


def run():
    """Main entry point for remote network tools"""
    tools = RemoteNetworkTools()
    
    console.print(Panel.fit(
        "[bold cyan]Remote Network Tools[/bold cyan]\n"
        "Network diagnostics on remote devices",
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
            title="Network Tools",
            text="Select operation:",
            values=[
                ("interfaces", "🌐  Network Interfaces"),
                ("ping", "📡  Ping Host"),
                ("traceroute", "🛤️  Traceroute"),
                ("routes", "🗺️  Routing Table"),
                ("ports", "🔌  Listening Ports"),
                ("connections", "🔗  Active Connections"),
                ("dns", "🔍  DNS Lookup"),
                ("stats", "📊  Network Statistics"),
                ("port_test", "🔧  Test Port"),
                ("firewall", "🔒  Firewall Rules"),
                ("bandwidth", "📈  Bandwidth Usage"),
                ("exit", "❌  Exit"),
            ],
            style=PT_DARK_STYLE,
        ).run()
        
        if operation == "interfaces":
            result = tools.get_network_interfaces()
            if 'output' in result:
                console.print(Panel(result['output'], title="Network Interfaces", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "ping":
            target = Prompt.ask("[cyan]Target host[/cyan]")
            count = Prompt.ask("[cyan]Number of pings[/cyan]", default="4")
            console.print("\n[cyan]Pinging...[/cyan]")
            result = tools.ping_host(target, int(count))
            if 'output' in result:
                console.print(Panel(result['output'], title=f"Ping {target}", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "traceroute":
            target = Prompt.ask("[cyan]Target host[/cyan]")
            console.print("\n[cyan]Running traceroute...[/cyan]")
            result = tools.traceroute(target)
            if 'output' in result:
                console.print(Panel(result['output'], title=f"Traceroute to {target}", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "routes":
            result = tools.get_routing_table()
            if 'output' in result:
                console.print(Panel(result['output'], title="Routing Table", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "ports":
            result = tools.get_listening_ports()
            if 'output' in result:
                console.print(Panel(result['output'], title="Listening Ports", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "connections":
            result = tools.get_active_connections()
            if 'output' in result:
                console.print(Panel(result['output'], title="Active Connections", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "dns":
            domain = Prompt.ask("[cyan]Domain name[/cyan]")
            console.print("\n[cyan]Looking up DNS...[/cyan]")
            result = tools.dns_lookup(domain)
            if 'output' in result:
                console.print(Panel(result['output'], title=f"DNS Lookup: {domain}", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "stats":
            result = tools.get_network_stats()
            if 'output' in result:
                console.print(Panel(result['output'], title="Network Statistics", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "port_test":
            host_target = Prompt.ask("[cyan]Host[/cyan]")
            port = Prompt.ask("[cyan]Port[/cyan]")
            console.print("\n[cyan]Testing port...[/cyan]")
            result = tools.test_port(host_target, port)
            if 'output' in result:
                console.print(Panel(result['output'], title=f"Port Test: {host_target}:{port}", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "firewall":
            result = tools.get_firewall_rules()
            if 'output' in result:
                console.print(Panel(result['output'], title="Firewall Rules", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "bandwidth":
            console.print("\n[cyan]Fetching bandwidth usage...[/cyan]")
            result = tools.get_bandwidth_usage()
            if 'output' in result:
                console.print(Panel(result['output'], title="Bandwidth Usage", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "exit" or operation is None:
            break
    
    tools.disconnect()
    console.print("[green]Disconnected from remote device[/green]")
    Prompt.ask("\nPress Enter to continue")


if __name__ == "__main__":
    run()
