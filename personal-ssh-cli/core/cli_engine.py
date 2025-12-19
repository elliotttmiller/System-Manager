"""
CLI Engine - Main Command Line Interface

Primary entry point and command processor for the SSH/SCP CLI system.
"""
import sys
import click
from rich.console import Console
from rich.table import Table
from pathlib import Path
from typing import Optional

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config_manager import ConfigManager
from core.connection_manager import ConnectionManager
from core.session_manager import SessionManager
from core.file_transfer import FileTransfer
from security.auth_manager import AuthManager
from security.device_whitelist import DeviceWhitelist
from interface.terminal_ui import TerminalUI


console = Console()


class CLIEngine:
    """Main CLI engine for the system."""
    
    def __init__(self):
        """Initialize CLI engine."""
        self.config_manager = None
        self.connection_manager = None
        self.session_manager = None
        self.auth_manager = None
        self.device_whitelist = None
        self.ui = TerminalUI()
        self.initialized = False
    
    def initialize(self, config_dir: Optional[Path] = None):
        """Initialize the system.
        
        Args:
            config_dir: Optional custom configuration directory
        """
        if self.initialized:
            return
        
        try:
            self.config_manager = ConfigManager(config_dir)
            self.config_manager.initialize()
            
            self.connection_manager = ConnectionManager(self.config_manager)
            self.session_manager = SessionManager(self.config_manager)
            self.auth_manager = AuthManager(self.config_manager)
            self.device_whitelist = DeviceWhitelist(self.config_manager)
            
            self.initialized = True
            
        except Exception as e:
            console.print(f"[red]Failed to initialize system: {e}[/red]")
            sys.exit(1)


# Create global CLI engine instance
cli_engine = CLIEngine()


@click.group()
@click.option('--config-dir', type=click.Path(), help='Custom configuration directory')
def cli(config_dir):
    """Personal SSH/SCP CLI System Manager
    
    A comprehensive command-line interface for managing SSH connections
    and file transfers across your personal devices.
    """
    cli_engine.initialize(Path(config_dir) if config_dir else None)


@cli.command()
@click.argument('profile_name')
def connect(profile_name: str):
    """Connect to a device using a saved profile.
    
    \b
    Examples:
        pssh connect home-server
        pssh connect work-laptop
    """
    try:
        # Create connection
        conn_id = cli_engine.connection_manager.create_connection(profile_name)
        
        console.print(f"[yellow]Connecting to {profile_name}...[/yellow]")
        
        # Establish connection
        if cli_engine.connection_manager.connect(conn_id):
            console.print(f"[green]✓ Connected to {profile_name}[/green]")
            
            # Create session
            session_id = cli_engine.session_manager.create_session(conn_id, profile_name)
            console.print(f"[blue]Session ID: {session_id}[/blue]")
        else:
            console.print(f"[red]Failed to connect to {profile_name}[/red]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
def disconnect():
    """Disconnect all active connections."""
    try:
        cli_engine.connection_manager.disconnect_all()
        console.print("[green]✓ All connections closed[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument('connection_id')
@click.argument('command')
def exec(connection_id: str, command: str):
    """Execute a command on a remote connection.
    
    \b
    Examples:
        pssh exec conn_1 "ls -la"
        pssh exec conn_1 "ps aux"
    """
    try:
        result = cli_engine.connection_manager.execute_command(connection_id, command)
        
        if result['exit_code'] == 0:
            console.print("[green]Command output:[/green]")
            console.print(result['stdout'])
        else:
            console.print(f"[red]Command failed with exit code {result['exit_code']}[/red]")
            if result['stderr']:
                console.print(f"[red]{result['stderr']}[/red]")
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
def list_connections():
    """List all active connections."""
    try:
        connections = cli_engine.connection_manager.list_connections()
        
        if not connections:
            console.print("[yellow]No active connections[/yellow]")
            return
        
        table = Table(title="Active Connections")
        table.add_column("ID", style="cyan")
        table.add_column("Host", style="green")
        table.add_column("User", style="blue")
        table.add_column("Status", style="yellow")
        
        for conn in connections:
            status = "Connected" if conn['connected'] and conn['alive'] else "Disconnected"
            table.add_row(
                conn['id'],
                conn['hostname'],
                conn['username'],
                status
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
def list_profiles():
    """List all saved device profiles."""
    try:
        profiles = cli_engine.config_manager.list_profiles()
        
        if not profiles:
            console.print("[yellow]No profiles configured[/yellow]")
            console.print("\nUse 'pssh add-profile' to create a new profile")
            return
        
        table = Table(title="Device Profiles")
        table.add_column("Name", style="cyan")
        
        for profile_name in profiles:
            table.add_row(profile_name)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument('name')
@click.option('--hostname', prompt=True, help='Hostname or IP address')
@click.option('--username', prompt=True, help='SSH username')
@click.option('--port', default=22, help='SSH port')
@click.option('--key-file', type=click.Path(exists=True), help='Path to SSH key file')
def add_profile(name: str, hostname: str, username: str, port: int, key_file: Optional[str]):
    """Add a new device profile.
    
    \b
    Examples:
        pssh add-profile home-server --hostname 192.168.1.100 --username user
        pssh add-profile work-laptop --hostname work.example.com --username admin
    """
    try:
        profile = {
            'hostname': hostname,
            'username': username,
            'port': port,
            'verify_host_keys': True,
            'compression': True,
        }
        
        if key_file:
            profile['key_file'] = key_file
        
        cli_engine.config_manager.add_profile(name, profile)
        console.print(f"[green]✓ Profile '{name}' added successfully[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument('name')
def delete_profile(name: str):
    """Delete a device profile.
    
    \b
    Examples:
        pssh delete-profile old-server
    """
    try:
        if cli_engine.config_manager.delete_profile(name):
            console.print(f"[green]✓ Profile '{name}' deleted[/green]")
        else:
            console.print(f"[yellow]Profile '{name}' not found[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument('connection_id')
@click.argument('local_path')
@click.argument('remote_path')
@click.option('--verify/--no-verify', default=True, help='Verify file integrity')
def upload(connection_id: str, local_path: str, remote_path: str, verify: bool):
    """Upload a file to a remote system.
    
    \b
    Examples:
        pssh upload conn_1 /local/file.txt /remote/file.txt
        pssh upload conn_1 ./document.pdf ~/documents/
    """
    try:
        connection = cli_engine.connection_manager.get_connection(connection_id)
        if not connection:
            console.print(f"[red]Connection '{connection_id}' not found[/red]")
            return
        
        file_transfer = FileTransfer(connection)
        
        console.print(f"[yellow]Uploading {local_path} to {remote_path}...[/yellow]")
        
        result = file_transfer.upload_file(local_path, remote_path, verify=verify)
        
        if result['success']:
            console.print(f"[green]✓ File uploaded successfully[/green]")
            console.print(f"  Size: {result['size']} bytes")
            if verify:
                console.print(f"  Checksum: {result['checksum']}")
        else:
            console.print(f"[red]Upload failed: {result['error']}[/red]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument('connection_id')
@click.argument('remote_path')
@click.argument('local_path')
@click.option('--verify/--no-verify', default=True, help='Verify file integrity')
def download(connection_id: str, remote_path: str, local_path: str, verify: bool):
    """Download a file from a remote system.
    
    \b
    Examples:
        pssh download conn_1 /remote/file.txt /local/file.txt
        pssh download conn_1 ~/logs/app.log ./logs/
    """
    try:
        connection = cli_engine.connection_manager.get_connection(connection_id)
        if not connection:
            console.print(f"[red]Connection '{connection_id}' not found[/red]")
            return
        
        file_transfer = FileTransfer(connection)
        
        console.print(f"[yellow]Downloading {remote_path} to {local_path}...[/yellow]")
        
        result = file_transfer.download_file(remote_path, local_path, verify=verify)
        
        if result['success']:
            console.print(f"[green]✓ File downloaded successfully[/green]")
            console.print(f"  Size: {result['size']} bytes")
            if verify:
                console.print(f"  Checksum: {result['checksum']}")
        else:
            console.print(f"[red]Download failed: {result['error']}[/red]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
def list_sessions():
    """List all active sessions."""
    try:
        sessions = cli_engine.session_manager.list_sessions()
        
        if not sessions:
            console.print("[yellow]No active sessions[/yellow]")
            return
        
        table = Table(title="Sessions")
        table.add_column("ID", style="cyan")
        table.add_column("Profile", style="green")
        table.add_column("State", style="yellow")
        table.add_column("Created", style="blue")
        table.add_column("Commands", style="magenta")
        
        for session in sessions:
            table.add_row(
                session['session_id'],
                session['profile_name'],
                session['state'],
                session['created_at'],
                str(session['commands_count'])
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
def version():
    """Display version information."""
    console.print(f"[green]Personal SSH/SCP CLI System Manager v1.0.0[/green]")


@cli.command()
def setup():
    """Run interactive setup wizard."""
    console.print("[bold blue]Personal SSH/SCP CLI Setup Wizard[/bold blue]")
    console.print("\nWelcome! Let's configure your SSH CLI system.\n")
    
    try:
        # Check for existing SSH keys
        ssh_dir = Path.home() / ".ssh"
        if ssh_dir.exists():
            console.print("[green]✓ Found existing .ssh directory[/green]")
            
            key_files = list(ssh_dir.glob("id_*"))
            if key_files:
                console.print(f"[green]✓ Found {len(key_files)} SSH key(s)[/green]")
        else:
            console.print("[yellow]! No .ssh directory found[/yellow]")
            console.print("  You may need to generate SSH keys")
        
        # Initialize configuration
        cli_engine.config_manager.initialize()
        console.print("[green]✓ Configuration initialized[/green]")
        
        console.print("\n[bold green]Setup complete![/bold green]")
        console.print("\nNext steps:")
        console.print("  1. Add a device profile: pssh add-profile <name>")
        console.print("  2. Connect to a device: pssh connect <profile-name>")
        console.print("  3. View help: pssh --help")
        
    except Exception as e:
        console.print(f"[red]Setup failed: {e}[/red]")


def main():
    """Main entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()
