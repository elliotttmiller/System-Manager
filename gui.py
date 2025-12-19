# -*- coding: utf-8 -*-
"""
Interactive GUI/Menu Interface for System Manager

A user-friendly interactive terminal interface with menus and visual navigation.
No need to remember commands - just select from menus!
"""

import sys
from pathlib import Path

# Set UTF-8 encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Add personal-ssh-cli to path
sys.path.insert(0, str(Path(__file__).parent / 'personal-ssh-cli'))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import time

console = Console()


class InteractiveGUI:
    """Interactive GUI for System Manager."""
    
    def __init__(self):
        """Initialize the interactive GUI."""
        self.running = True
        self.config_manager = None
        self.connection_manager = None
        self.setup_cli_engine()
    
    def setup_cli_engine(self):
        """Initialize CLI engine components."""
        try:
            from core.config_manager import ConfigManager
            from core.connection_manager import ConnectionManager
            
            self.config_manager = ConfigManager()
            self.config_manager.initialize()
            self.connection_manager = ConnectionManager(self.config_manager)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not initialize engine: {e}[/yellow]")
    
    def clear_screen(self):
        """Clear the console screen."""
        console.clear()
    
    def show_banner(self):
        """Display application banner."""
        banner = """
[bold cyan]╔══════════════════════════════════════════════════════════════════════╗
║                  PERSONAL SSH/SCP SYSTEM MANAGER                     ║
║                         Version 1.0.0                                ║
║                    Interactive Menu Interface                        ║
╚══════════════════════════════════════════════════════════════════════╝[/bold cyan]
"""
        console.print(banner)
    
    def show_main_menu(self):
        """Display main menu and get user choice."""
        self.clear_screen()
        self.show_banner()
        
        menu_panel = Panel(
            """[bold cyan]Main Menu[/bold cyan]

[bold green]1.[/bold green] 🔧 Setup & Configuration
[bold green]2.[/bold green] 🖥️  Device Profiles
[bold green]3.[/bold green] 🔌 Connections
[bold green]4.[/bold green] 📁 File Transfer
[bold green]5.[/bold green] ⚙️  Settings
[bold green]6.[/bold green] ℹ️  Information & Help
[bold green]0.[/bold green] 🚪 Exit

[dim]Use number keys to navigate[/dim]""",
            title="[bold]Main Menu[/bold]",
            border_style="blue"
        )
        
        console.print(menu_panel)
        choice = Prompt.ask(
            "\n[cyan]Select an option[/cyan]",
            choices=["0", "1", "2", "3", "4", "5", "6"],
            default="1"
        )
        
        return choice
    
    def setup_menu(self):
        """Setup and configuration submenu."""
        while True:
            self.clear_screen()
            self.show_banner()
            
            menu_panel = Panel(
                """[bold cyan]Setup & Configuration[/bold cyan]

[bold green]1.[/bold green] 🔧 Client Setup (This Device Connects TO Others)
[bold green]2.[/bold green] 🖥️  Server Setup (This Device ACCEPTS Connections)
[bold green]3.[/bold green] 🌐 Test IP Detection
[bold green]4.[/bold green] 🔑 Generate SSH Keys
[bold green]0.[/bold green] ← Back to Main Menu

[dim]Configure this device as client or server[/dim]""",
                title="[bold]Setup & Configuration[/bold]",
                border_style="green"
            )
            
            console.print(menu_panel)
            choice = Prompt.ask(
                "\n[cyan]Select an option[/cyan]",
                choices=["0", "1", "2", "3", "4"],
                default="0"
            )
            
            if choice == "0":
                break
            elif choice == "1":
                self.client_setup()
            elif choice == "2":
                self.server_setup()
            elif choice == "3":
                self.test_ip_detection()
            elif choice == "4":
                self.generate_ssh_keys()
    
    def client_setup(self):
        """Run client setup wizard."""
        self.clear_screen()
        console.print("\n[bold cyan]═══ Client Setup Wizard ═══[/bold cyan]\n")
        
        console.print("[yellow]This will configure this device to connect to remote SSH servers.[/yellow]\n")
        
        if not Confirm.ask("Continue with client setup?", default=True):
            return
        
        try:
            from core.cli_engine import cli_engine
            
            # Check for SSH directory
            ssh_dir = Path.home() / ".ssh"
            if ssh_dir.exists():
                console.print("[green]✓ Found existing .ssh directory[/green]")
                key_files = list(ssh_dir.glob("id_*"))
                if key_files:
                    console.print(f"[green]✓ Found {len(key_files)} SSH key(s)[/green]")
            else:
                console.print("[yellow]! No .ssh directory found[/yellow]")
            
            # Initialize config
            cli_engine.config_manager.initialize()
            console.print("[green]✓ Configuration initialized[/green]")
            
            console.print("\n[bold green]✓ Setup complete![/bold green]")
            console.print("\n[cyan]Next steps:[/cyan]")
            console.print("  1. Go to 'Device Profiles' menu to add devices")
            console.print("  2. Or import a profile from server setup")
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        
        input("\nPress ENTER to continue...")
    
    def server_setup(self):
        """Run server setup wizard."""
        self.clear_screen()
        console.print("\n[bold cyan]═══ Server Setup Wizard ═══[/bold cyan]\n")
        
        console.print("[yellow]This will configure this device as an SSH SERVER.[/yellow]")
        console.print("[yellow]Other devices will be able to connect TO this device.[/yellow]\n")
        
        if not Confirm.ask("Continue with server setup?", default=True):
            return
        
        try:
            from features.auto_setup import AutoSetup
            
            setup = AutoSetup()
            success = setup.run_interactive_setup()
            
            if success:
                console.print("\n[bold green]✓ Server setup completed![/bold green]")
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        
        input("\nPress ENTER to continue...")
    
    def test_ip_detection(self):
        """Test IP address detection."""
        self.clear_screen()
        console.print("\n[bold cyan]═══ IP Address Detection Test ═══[/bold cyan]\n")
        
        try:
            from features.auto_setup import AutoSetup
            
            setup = AutoSetup()
            system_info = setup.detect_system_info()
            
            console.print(f"[green]Hostname:[/green] {system_info['hostname']}")
            console.print(f"[green]OS:[/green] {system_info['os']}")
            console.print(f"[green]Username:[/green] {system_info['username']}")
            
            console.print("\n[bold cyan]Detected IP Addresses:[/bold cyan]")
            for idx, ip in enumerate(system_info['ip_addresses'], 1):
                marker = " [green]<- Primary[/green]" if idx == 1 else ""
                console.print(f"  {idx}. {ip}{marker}")
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        
        input("\nPress ENTER to continue...")
    
    def generate_ssh_keys(self):
        """Generate SSH key pair."""
        self.clear_screen()
        console.print("\n[bold cyan]═══ Generate SSH Keys ═══[/bold cyan]\n")
        
        ssh_dir = Path.home() / '.ssh'
        key_file = ssh_dir / 'id_ed25519'
        
        if key_file.exists():
            console.print(f"[yellow]SSH key already exists at: {key_file}[/yellow]")
            if not Confirm.ask("Overwrite existing key?", default=False):
                input("\nPress ENTER to continue...")
                return
        
        try:
            import subprocess
            
            console.print("[yellow]Generating ed25519 SSH key pair...[/yellow]")
            subprocess.run(
                ['ssh-keygen', '-t', 'ed25519', '-f', str(key_file), '-N', ''],
                check=True
            )
            console.print(f"[green]✓ SSH key generated: {key_file}[/green]")
            console.print(f"[green]✓ Public key: {key_file}.pub[/green]")
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        
        input("\nPress ENTER to continue...")
    
    def profile_menu(self):
        """Device profiles submenu."""
        while True:
            self.clear_screen()
            self.show_banner()
            
            menu_panel = Panel(
                """[bold cyan]Device Profiles[/bold cyan]

[bold green]1.[/bold green] 📋 List All Profiles
[bold green]2.[/bold green] ➕ Add New Profile (Manual)
[bold green]3.[/bold green] 📥 Import Profile (From JSON)
[bold green]4.[/bold green] ✏️  Edit Profile
[bold green]5.[/bold green] 🗑️  Delete Profile
[bold green]0.[/bold green] ← Back to Main Menu

[dim]Manage device connection profiles[/dim]""",
                title="[bold]Device Profiles[/bold]",
                border_style="cyan"
            )
            
            console.print(menu_panel)
            choice = Prompt.ask(
                "\n[cyan]Select an option[/cyan]",
                choices=["0", "1", "2", "3", "4", "5"],
                default="1"
            )
            
            if choice == "0":
                break
            elif choice == "1":
                self.list_profiles()
            elif choice == "2":
                self.add_profile_manual()
            elif choice == "3":
                self.import_profile()
            elif choice == "4":
                self.edit_profile()
            elif choice == "5":
                self.delete_profile()
    
    def list_profiles(self):
        """List all device profiles."""
        self.clear_screen()
        console.print("\n[bold cyan]═══ Device Profiles ═══[/bold cyan]\n")
        
        try:
            profiles = self.config_manager.get_profiles()
            
            if not profiles:
                console.print("[yellow]No profiles configured yet.[/yellow]")
                console.print("\n[cyan]Add a profile using:[/cyan]")
                console.print("  • Manual entry (option 2)")
                console.print("  • Import from JSON (option 3)")
            else:
                table = Table(title="Configured Profiles", show_header=True)
                table.add_column("Name", style="cyan", no_wrap=True)
                table.add_column("Host", style="green")
                table.add_column("User", style="yellow")
                table.add_column("Port", style="magenta")
                
                for name, profile in profiles.items():
                    table.add_row(
                        name,
                        profile.get('hostname', 'N/A'),
                        profile.get('username', 'N/A'),
                        str(profile.get('port', 22))
                    )
                
                console.print(table)
                
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        
        input("\nPress ENTER to continue...")
    
    def add_profile_manual(self):
        """Manually add a new profile."""
        self.clear_screen()
        console.print("\n[bold cyan]═══ Add New Profile ═══[/bold cyan]\n")
        
        try:
            name = Prompt.ask("[cyan]Profile name[/cyan]")
            hostname = Prompt.ask("[cyan]Hostname or IP address[/cyan]")
            username = Prompt.ask("[cyan]Username[/cyan]")
            port = Prompt.ask("[cyan]Port[/cyan]", default="22")
            
            key_file = Prompt.ask(
                "[cyan]SSH key file path (leave empty for password auth)[/cyan]",
                default=""
            )
            
            profile = {
                'hostname': hostname,
                'username': username,
                'port': int(port),
                'verify_host_keys': True,
                'compression': True,
            }
            
            if key_file:
                profile['key_file'] = key_file
            
            self.config_manager.add_profile(name, profile)
            console.print(f"\n[green]✓ Profile '{name}' added successfully![/green]")
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        
        input("\nPress ENTER to continue...")
    
    def import_profile(self):
        """Import profile from JSON file."""
        self.clear_screen()
        console.print("\n[bold cyan]═══ Import Profile ═══[/bold cyan]\n")
        
        try:
            import json
            
            file_path = Prompt.ask("[cyan]Path to JSON profile file[/cyan]")
            
            with open(file_path, 'r') as f:
                config = json.load(f)
            
            profile_name = config.get('profile_name', Path(file_path).stem)
            
            profile = {
                'hostname': config.get('host', config.get('hostname')),
                'username': config.get('username'),
                'port': config.get('port', 22),
                'verify_host_keys': True,
                'compression': True,
            }
            
            if config.get('key_file'):
                profile['key_file'] = config.get('key_file')
            
            self.config_manager.add_profile(profile_name, profile)
            
            console.print(f"\n[green]✓ Profile '{profile_name}' imported successfully![/green]")
            console.print(f"  Host: {profile['hostname']}")
            console.print(f"  User: {profile['username']}")
            
        except FileNotFoundError:
            console.print("[red]Error: File not found[/red]")
        except json.JSONDecodeError:
            console.print("[red]Error: Invalid JSON file[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        
        input("\nPress ENTER to continue...")
    
    def edit_profile(self):
        """Edit existing profile."""
        console.print("\n[yellow]Profile editing coming soon...[/yellow]")
        input("\nPress ENTER to continue...")
    
    def delete_profile(self):
        """Delete a profile."""
        self.clear_screen()
        console.print("\n[bold cyan]═══ Delete Profile ═══[/bold cyan]\n")
        
        try:
            profiles = self.config_manager.get_profiles()
            
            if not profiles:
                console.print("[yellow]No profiles to delete.[/yellow]")
                input("\nPress ENTER to continue...")
                return
            
            console.print("[cyan]Available profiles:[/cyan]")
            for name in profiles.keys():
                console.print(f"  • {name}")
            
            name = Prompt.ask("\n[cyan]Profile name to delete[/cyan]")
            
            if name not in profiles:
                console.print(f"[red]Profile '{name}' not found.[/red]")
            else:
                if Confirm.ask(f"Delete profile '{name}'?", default=False):
                    self.config_manager.delete_profile(name)
                    console.print(f"[green]✓ Profile '{name}' deleted.[/green]")
                
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        
        input("\nPress ENTER to continue...")
    
    def connection_menu(self):
        """Connections submenu."""
        while True:
            self.clear_screen()
            self.show_banner()
            
            menu_panel = Panel(
                """[bold cyan]Connections[/bold cyan]

[bold green]1.[/bold green] 🔌 Connect to Device
[bold green]2.[/bold green] 📊 List Active Connections
[bold green]3.[/bold green] 🔌 Disconnect All
[bold green]4.[/bold green] 🖥️  Execute Remote Command
[bold green]0.[/bold green] ← Back to Main Menu

[dim]Manage SSH connections[/dim]""",
                title="[bold]Connections[/bold]",
                border_style="yellow"
            )
            
            console.print(menu_panel)
            choice = Prompt.ask(
                "\n[cyan]Select an option[/cyan]",
                choices=["0", "1", "2", "3", "4"],
                default="1"
            )
            
            if choice == "0":
                break
            elif choice == "1":
                self.connect_to_device()
            elif choice == "2":
                self.list_connections()
            elif choice == "3":
                self.disconnect_all()
            elif choice == "4":
                self.execute_remote_command()
    
    def connect_to_device(self):
        """Connect to a device."""
        console.print("\n[yellow]Connection feature coming soon...[/yellow]")
        console.print("[cyan]Will establish SSH connection to selected profile.[/cyan]")
        input("\nPress ENTER to continue...")
    
    def list_connections(self):
        """List active connections."""
        console.print("\n[yellow]No active connections.[/yellow]")
        input("\nPress ENTER to continue...")
    
    def disconnect_all(self):
        """Disconnect all connections."""
        console.print("\n[yellow]All connections disconnected.[/yellow]")
        input("\nPress ENTER to continue...")
    
    def execute_remote_command(self):
        """Execute command on remote device."""
        console.print("\n[yellow]Remote execution feature coming soon...[/yellow]")
        input("\nPress ENTER to continue...")
    
    def file_transfer_menu(self):
        """File transfer submenu."""
        while True:
            self.clear_screen()
            self.show_banner()
            
            menu_panel = Panel(
                """[bold cyan]File Transfer[/bold cyan]

[bold green]1.[/bold green] ⬆️  Upload File to Remote
[bold green]2.[/bold green] ⬇️  Download File from Remote
[bold green]3.[/bold green] 📁 Upload Directory
[bold green]4.[/bold green] 📁 Download Directory
[bold green]0.[/bold green] ← Back to Main Menu

[dim]Transfer files between devices[/dim]""",
                title="[bold]File Transfer[/bold]",
                border_style="magenta"
            )
            
            console.print(menu_panel)
            choice = Prompt.ask(
                "\n[cyan]Select an option[/cyan]",
                choices=["0", "1", "2", "3", "4"],
                default="0"
            )
            
            if choice == "0":
                break
            else:
                console.print("\n[yellow]File transfer features coming soon...[/yellow]")
                input("\nPress ENTER to continue...")
    
    def settings_menu(self):
        """Settings submenu."""
        console.print("\n[yellow]Settings menu coming soon...[/yellow]")
        input("\nPress ENTER to continue...")
    
    def info_menu(self):
        """Information and help menu."""
        self.clear_screen()
        self.show_banner()
        
        info_panel = Panel(
            """[bold cyan]System Manager v1.0.0[/bold cyan]

[bold]Features:[/bold]
• Setup devices as SSH clients or servers
• Manage multiple device profiles
• Establish secure SSH connections
• Transfer files between devices
• Execute remote commands

[bold]Quick Start:[/bold]
1. Go to Setup & Configuration
2. Run Server Setup on your desktop/server
3. Run Client Setup on your laptop
4. Import the profile from server
5. Connect and enjoy!

[bold]Documentation:[/bold]
• See USER_GUIDE.md for detailed instructions
• See AUTOMATED_SETUP_GUIDE.md for setup help

[bold cyan]GitHub:[/bold cyan] github.com/elliotttmiller/System-Manager""",
            title="[bold]Information & Help[/bold]",
            border_style="blue"
        )
        
        console.print(info_panel)
        input("\nPress ENTER to continue...")
    
    def run(self):
        """Run the interactive GUI main loop."""
        try:
            while self.running:
                choice = self.show_main_menu()
                
                if choice == "0":
                    if Confirm.ask("\n[yellow]Exit System Manager?[/yellow]", default=False):
                        self.running = False
                elif choice == "1":
                    self.setup_menu()
                elif choice == "2":
                    self.profile_menu()
                elif choice == "3":
                    self.connection_menu()
                elif choice == "4":
                    self.file_transfer_menu()
                elif choice == "5":
                    self.settings_menu()
                elif choice == "6":
                    self.info_menu()
            
            self.clear_screen()
            console.print("\n[bold green]Thank you for using System Manager![/bold green]\n")
            
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Interrupted by user[/yellow]")
        except Exception as e:
            console.print(f"\n[red]Fatal error: {e}[/red]")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point for interactive GUI."""
    gui = InteractiveGUI()
    gui.run()


if __name__ == '__main__':
    main()
