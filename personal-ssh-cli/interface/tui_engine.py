#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TUI Engine - Interactive Terminal User Interface
Orchestrates all features and services in a clean, modern interface.
"""

import sys
import time
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.text import Text
from rich.theme import Theme
from rich.style import Style
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.styles import Style as PTStyle
import importlib
import importlib.util
import os

# Import core modules
from core.config_manager import ConfigManager
from core.connection_manager import ConnectionManager
from core.session_manager import SessionManager
from core.file_transfer import FileTransfer

# Import feature modules
from features.auto_setup import AutoSetup
from features.device_discovery import DeviceDiscovery
from features.monitoring import ConnectionMonitor, TransferMonitor, SystemMonitor

# Import security modules
from security.audit_logger import AuditLogger
from security.auth_manager import AuthManager

# Custom dark theme
DARK_THEME = Theme({
    "primary": "bold cyan",
    "secondary": "bright_blue",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "info": "bright_white",
    "dim": "dim white",
    "accent": "magenta",
    "border": "bright_black",
})

# Comprehensive Prompt Toolkit dark theme style
PT_DARK_STYLE = PTStyle.from_dict({
    # Dialog window
    'dialog': 'bg:#1a1a1a #00d7ff',
    'dialog.body': 'bg:#1a1a1a #e0e0e0',
    'dialog frame.label': 'bg:#1a1a1a #00d7ff bold',
    'dialog shadow': 'bg:#000000',
    
    # Radio list (menu items)
    'radiolist': 'bg:#1a1a1a #e0e0e0',
    'radiolist focused': 'bg:#00d7ff #000000 bold',
    'radiolist selected': 'bg:#1a1a1a #00ff87',
    
    # Text and labels
    'text': 'bg:#1a1a1a #e0e0e0',
    'label': 'bg:#1a1a1a #00d7ff',
    
    # Button elements
    'button': 'bg:#1a1a1a #00d7ff',
    'button.focused': 'bg:#00d7ff #000000 bold',
    
    # Input fields
    'text-area': 'bg:#1a1a1a #e0e0e0',
    'text-area.prompt': 'bg:#1a1a1a #00d7ff',
    
    # Borders and frames
    'frame.border': 'bg:#1a1a1a #00d7ff',
    'frame.label': 'bg:#1a1a1a #00d7ff bold',
})


class TUIEngine:
    """
    Main TUI Engine that orchestrates all features and services.
    Provides a clean, modern interface with dark theme and smooth animations.
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize TUI Engine with all required managers."""
        self.console = Console(theme=DARK_THEME)
        self.config_dir = config_dir
        
        # Initialize managers
        self.config_mgr = None
        self.conn_mgr = None
        self.session_mgr = None
        
        # Feature flags
        self.running = True
        
        # Load local and remote features dynamically
        self.local_features = self.load_features("local")
        self.remote_features = self.load_features("remote")
        
    def load_features(self, feature_type):
        """Dynamically load features from the specified directory."""
        features = {}
        base_path = os.path.join(os.path.dirname(__file__), "..", feature_type)
        base_path = os.path.abspath(base_path)
        
        if not os.path.exists(base_path):
            self.console.print(f"[warning]⚠️  Feature directory not found: {base_path}[/warning]")
            return features
            
        for file in os.listdir(base_path):
            if file.endswith(".py") and file != "__init__.py":
                module_name = file[:-3]
                module_file_path = os.path.join(base_path, file)
                try:
                    # Load module directly from file path
                    spec = importlib.util.spec_from_file_location(module_name, module_file_path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[f"{feature_type}.{module_name}"] = module
                    spec.loader.exec_module(module)
                    features[module_name] = module
                except Exception as e:
                    self.console.print(f"[error]Failed to load {module_name}: {e}[/error]")
        return features

    def initialize(self):
        """Initialize all managers and services with loading animation."""
        self.clear_screen()
        
        # Show loading animation
        with Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[primary]Initializing..."),
            transient=True,
            console=self.console
        ) as progress:
            task = progress.add_task("init", total=3)
            
            try:
                # Load config manager
                progress.update(task, description="[primary]Loading configuration...")
                time.sleep(0.3)  # Smooth transition
                self.config_mgr = ConfigManager(self.config_dir)
                self.config_mgr.initialize()
                progress.advance(task)
                
                # Load connection manager
                progress.update(task, description="[primary]Initializing connections...")
                time.sleep(0.2)
                self.conn_mgr = ConnectionManager(self.config_mgr)
                progress.advance(task)
                
                # Load session manager
                progress.update(task, description="[primary]Preparing session manager...")
                time.sleep(0.2)
                self.session_mgr = SessionManager(self.config_mgr)
                progress.advance(task)
                
                return True
            except Exception as e:
                self.console.print(f"[error]✗ Initialization error: {e}[/error]")
                return False
    
    def clear_screen(self):
        """Clear screen with smooth effect."""
        self.console.clear()
        time.sleep(0.05)  # Brief pause for smooth transition
    
    def run(self):
        """Main TUI loop."""
        if not self.initialize():
            return
        
        while self.running:
            try:
                choice = self.show_main_menu()
                self.handle_menu_choice(choice)
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupted by user[/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
                Prompt.ask("Press Enter to continue")
    
    def show_main_menu(self) -> Optional[str]:
        """Display main menu with modern design."""
        self.clear_screen()
        
        # Animated header
        header = Text()
        header.append("SSH ", style="bold bright_cyan")
        header.append("Manager", style="bold white")
        header.append(" ", style="")
        header.append("v1.0", style="dim")
        
        self.console.print()
        self.console.print(Panel(
            Align.center(header),
            border_style="border",
            padding=(0, 2)
        ))
        self.console.print()
        
        # Show menu with custom style
        return radiolist_dialog(
            title="",
            text="Navigate with arrow keys • Press Enter to select",
            values=[
                ("connections", "🔌  Connect to Device"),
                ("profiles", "📋  Manage Profiles"),
                ("setup", "⚙️   Setup New Device"),
                ("transfer", "📁  File Transfer"),
                ("sessions", "💻  Active Sessions"),
                ("advanced", "🔧  Advanced Features"),
                ("exit", "🚪  Exit"),
            ],
            style=PT_DARK_STYLE,
        ).run()
    
    def handle_menu_choice(self, choice: Optional[str]):
        """Route menu choice to appropriate handler."""
        if choice == "connections":
            self.show_connections()
        elif choice == "profiles":
            self.show_profiles()
        elif choice == "setup":
            self.show_setup()
        elif choice == "transfer":
            self.show_transfer()
        elif choice == "sessions":
            self.show_sessions()
        elif choice == "advanced":
            self.show_advanced()
        elif choice == "exit" or choice is None:
            self.exit_application()
    
    # ===== CONNECTION MANAGEMENT =====
    
    def show_connections(self):
        """Display and manage connections with enhanced UI."""
        self.clear_screen()
        
        # Animated section header
        self.console.print()
        title = Text("Available Connections", style="primary")
        self.console.print(Panel(title, border_style="border", padding=(0, 2)))
        self.console.print()
        
        try:
            # Show loading spinner
            with self.console.status("[primary]Loading profiles...", spinner="dots"):
                time.sleep(0.3)  # Smooth loading effect
                profiles = self.config_mgr.list_profiles()
            
            if not profiles:
                self.console.print(Panel(
                    "[warning]⚠️  No profiles found[/warning]\n\n"
                    "[info]Create a profile in Setup New Device to get started[/info]",
                    border_style="warning",
                    padding=(1, 2)
                ))
                self.console.print()
                Prompt.ask("[dim]Press Enter to continue[/dim]")
                return
            
            # Build selection list with status indicators
            values = []
            for profile in profiles:
                name = profile.get('name', 'Unknown')
                host = profile.get('host', 'N/A')
                user = profile.get('username', 'N/A')
                display = f"🖥️  {name}  [dim]→[/dim]  {user}@{host}"
                values.append((name, display))
            
            values.append(("back", "⬅️  Back to Main Menu"))
            
            result = radiolist_dialog(
                title="",
                text="Select a device to connect:",
                values=values,
                style=PT_DARK_STYLE,
            ).run()
            
            if result and result != "back":
                self.connect_to_device(result)
                
        except Exception as e:
            self.console.print(f"[error]✗ Error: {e}[/error]\n")
            Prompt.ask("[dim]Press Enter to continue[/dim]")
    
    def connect_to_device(self, profile_name: str):
        """Establish SSH connection with animated progress."""
        self.console.print()
        
        try:
            # Animated connection progress
            with Progress(
                SpinnerColumn(spinner_name="dots"),
                TextColumn("[primary]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Connecting to {profile_name}...", total=None)
                time.sleep(0.5)  # Connection animation
                
                session = self.conn_mgr.connect(profile_name)
                progress.stop()
            
            # Success message with effect
            self.console.print()
            self.console.print(Panel(
                "[success]✓ Connected successfully![/success]",
                border_style="success",
                padding=(0, 2)
            ))
            
            # Interactive shell session
            self.console.print("\n[info]Starting interactive session...[/info]")
            time.sleep(0.3)
            # TODO: Implement interactive shell
            
            self.console.print("[dim]Connection closed.[/dim]\n")
            
        except Exception as e:
            self.console.print()
            self.console.print(Panel(
                f"[error]✗ Connection failed[/error]\n\n[dim]{e}[/dim]",
                border_style="error",
                padding=(1, 2)
            ))
            self.console.print()
        
        Prompt.ask("[dim]Press Enter to continue[/dim]")
    
    # ===== PROFILE MANAGEMENT =====
    
    def show_profiles(self):
        """Display and manage device profiles with enhanced table."""
        while True:
            self.clear_screen()
            
            self.console.print()
            title = Text("Device Profiles", style="primary")
            self.console.print(Panel(title, border_style="border", padding=(0, 2)))
            self.console.print()
            
            try:
                with self.console.status("[primary]Loading profiles...", spinner="dots"):
                    time.sleep(0.2)
                    profiles = self.config_mgr.list_profiles()
                
                if profiles:
                    # Stylish table with gradient effect
                    table = Table(
                        show_header=True,
                        header_style="bold primary",
                        border_style="border",
                        row_styles=["", "dim"],
                        padding=(0, 1)
                    )
                    table.add_column("●", style="success", width=3)
                    table.add_column("Name", style="primary")
                    table.add_column("Host", style="info")
                    table.add_column("User", style="secondary")
                    table.add_column("Port", style="dim", justify="right")
                    
                    for profile in profiles:
                        table.add_row(
                            "●",
                            profile.get('name', 'N/A'),
                            profile.get('host', 'N/A'),
                            profile.get('username', 'N/A'),
                            str(profile.get('port', 22))
                        )
                    
                    self.console.print(table)
                    self.console.print()
                else:
                    self.console.print(Panel(
                        "[warning]⚠️  No profiles configured yet[/warning]\n\n"
                        "[info]Add a profile to get started[/info]",
                        border_style="warning",
                        padding=(1, 2)
                    ))
                    self.console.print()
                
                # Profile actions with icons
                result = radiolist_dialog(
                    title="",
                    text="Profile actions:",
                    values=[
                        ("add", "➕  Add New Profile"),
                        ("edit", "✏️   Edit Profile"),
                        ("delete", "🗑️   Delete Profile"),
                        ("back", "⬅️  Back"),
                    ],
                    style=PT_DARK_STYLE,
                ).run()
                
                if result == "add":
                    self.add_profile()
                elif result == "edit":
                    self.edit_profile()
                elif result == "delete":
                    self.delete_profile()
                elif result == "back" or result is None:
                    break
                    
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]\n")
                Prompt.ask("Press Enter to continue")
                break
    
    def add_profile(self):
        """Add new profile manually."""
        self.console.clear()
        self.console.print("\n[bold cyan]Create New Profile[/bold cyan]\n")
        
        try:
            name = Prompt.ask("[cyan]Profile name[/cyan]")
            host = Prompt.ask("[cyan]Hostname/IP[/cyan]")
            username = Prompt.ask("[cyan]Username[/cyan]")
            port = Prompt.ask("[cyan]Port[/cyan]", default="22")
            key_file = Prompt.ask("[cyan]SSH key file (optional)[/cyan]", default="")
            
            profile_data = {
                'name': name,
                'host': host,
                'username': username,
                'port': int(port),
            }
            
            if key_file:
                profile_data['key_file'] = key_file
            
            self.config_mgr.add_profile(name, profile_data)
            self.console.print(f"\n[green]✓ Profile '{name}' created successfully![/green]\n")
            
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]\n")
        
        Prompt.ask("Press Enter to continue")
    
    def edit_profile(self):
        """Edit existing profile."""
        self.console.clear()
        self.console.print("\n[bold cyan]Edit Profile[/bold cyan]\n")
        self.console.print("[yellow]Edit functionality coming soon![/yellow]\n")
        Prompt.ask("Press Enter to continue")
    
    def delete_profile(self):
        """Delete existing profile."""
        profiles = self.config_mgr.list_profiles()
        
        if not profiles:
            self.console.print("[yellow]No profiles to delete.[/yellow]\n")
            Prompt.ask("Press Enter to continue")
            return
        
        values = [(p['name'], f"🗑️  {p['name']}") for p in profiles]
        values.append(("cancel", "❌  Cancel"))
        
        result = radiolist_dialog(
            title="",
            text="Select profile to delete:",
            values=values,
            style=PT_DARK_STYLE,
        ).run()
        
        if result and result != "cancel":
            try:
                self.config_mgr.delete_profile(result)
                self.console.print(f"\n[green]✓ Profile '{result}' deleted.[/green]\n")
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]\n")
            
            Prompt.ask("Press Enter to continue")
    
    # ===== SETUP & CONFIGURATION =====
    
    def show_setup(self):
        """Setup new device with various methods."""
        self.clear_screen()
        
        self.console.print()
        title = Text("Setup New Device", style="primary")
        self.console.print(Panel(title, border_style="border", padding=(0, 2)))
        self.console.print()
        
        result = radiolist_dialog(
            title="",
            text="Choose setup method:",
            values=[
                ("auto", "🤖  Auto Setup (Detect & Configure)"),
                ("manual", "✍️   Manual Configuration"),
                ("import", "📥  Import SSH Config"),
                ("server", "🖥️   Setup SSH Server"),
                ("back", "⬅️  Back"),
            ],
            style=PT_DARK_STYLE,
        ).run()
        
        if result == "auto":
            self.run_auto_setup()
        elif result == "manual":
            self.add_profile()
        elif result == "import":
            self.import_ssh_config()
        elif result == "server":
            self.setup_ssh_server()
    
    def run_auto_setup(self):
        """Run automated device setup."""
        try:
            self.console.print("\n[cyan]Starting auto-setup...[/cyan]\n")
            
            auto_setup = AutoSetup()
            auto_setup.run_interactive_setup()
            
            self.console.print("\n[green]✓ Setup completed![/green]\n")
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]\n")
        
        Prompt.ask("Press Enter to continue")
    
    def import_ssh_config(self):
        """Import existing SSH config."""
        self.console.clear()
        self.console.print("\n[bold cyan]Import SSH Config[/bold cyan]\n")
        self.console.print("[yellow]SSH config import coming soon![/yellow]\n")
        Prompt.ask("Press Enter to continue")
    
    def setup_ssh_server(self):
        """Setup SSH server on local machine."""
        self.console.clear()
        self.console.print("\n[bold cyan]Setup SSH Server[/bold cyan]\n")
        self.console.print("[cyan]Configuring SSH server...[/cyan]\n")
        
        # Run server setup script
        try:
            import subprocess
            from pathlib import Path
            
            script_path = Path(__file__).parent.parent.parent / "setup_ssh_server.py"
            
            if script_path.exists():
                subprocess.run([sys.executable, str(script_path)])
            else:
                self.console.print("[yellow]Server setup script not found.[/yellow]\n")
                
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]\n")
        
        Prompt.ask("Press Enter to continue")
    
    # ===== FILE TRANSFER =====
    
    def show_transfer(self):
        """File transfer operations."""
        self.clear_screen()
        
        self.console.print()
        title = Text("File Transfer", style="primary")
        self.console.print(Panel(title, border_style="border", padding=(0, 2)))
        self.console.print()
        
        result = radiolist_dialog(
            title="",
            text="Choose transfer type:",
            values=[
                ("upload", "⬆️  Upload to Remote"),
                ("download", "⬇️  Download from Remote"),
                ("sync", "🔄  Sync Directories"),
                ("back", "⬅️  Back"),
            ],
            style=PT_DARK_STYLE,
        ).run()
        
        if result == "upload":
            self.upload_file()
        elif result == "download":
            self.download_file()
        elif result == "sync":
            self.console.print("\n[yellow]Directory sync coming soon![/yellow]\n")
            Prompt.ask("Press Enter to continue")
    
    def upload_file(self):
        """Upload file with animated progress."""
        self.clear_screen()
        
        self.console.print()
        title = Text("Upload File", style="primary")
        self.console.print(Panel(title, border_style="border", padding=(0, 2)))
        self.console.print()
        
        try:
            with self.console.status("[primary]Loading profiles...", spinner="dots"):
                time.sleep(0.2)
                profiles = self.config_mgr.list_profiles()
            
            if not profiles:
                self.console.print(Panel(
                    "[warning]⚠️  No profiles found[/warning]",
                    border_style="warning",
                    padding=(1, 2)
                ))
                self.console.print()
                Prompt.ask("[dim]Press Enter to continue[/dim]")
                return
            
            # Select profile with icons
            values = [(p['name'], f"📡  {p['name']}  [dim]→[/dim]  {p['host']}") for p in profiles]
            values.append(("cancel", "❌  Cancel"))
            
            profile_name = radiolist_dialog(
                title="",
                text="Select destination:",
                values=values,
                style=PT_DARK_STYLE,
            ).run()
            
            if profile_name == "cancel" or not profile_name:
                return
            
            local_path = Prompt.ask("[primary]📄 Local file path[/primary]")
            remote_path = Prompt.ask("[primary]📁 Remote destination[/primary]")
            
            # Animated upload
            self.console.print()
            with Progress(
                SpinnerColumn(spinner_name="dots"),
                TextColumn("[primary]{task.description}"),
                BarColumn(complete_style="success", finished_style="success"),
                TextColumn("[primary]{task.percentage:>3.0f}%"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Uploading {Path(local_path).name}...", total=100)
                
                connection = self.conn_mgr.connect(profile_name)
                transfer = FileTransfer(connection.client)
                
                # Simulate progress (replace with actual transfer progress)
                for i in range(100):
                    progress.update(task, advance=1)
                    time.sleep(0.02)
                
                transfer.upload(local_path, remote_path)
                connection.disconnect()
            
            self.console.print()
            self.console.print(Panel(
                "[success]✓ Upload completed successfully![/success]",
                border_style="success",
                padding=(0, 2)
            ))
            self.console.print()
            
        except Exception as e:
            self.console.print()
            self.console.print(Panel(
                f"[error]✗ Upload failed[/error]\n\n[dim]{e}[/dim]",
                border_style="error",
                padding=(1, 2)
            ))
            self.console.print()
        
        Prompt.ask("[dim]Press Enter to continue[/dim]")
    
    def download_file(self):
        """Download file from remote server."""
        self.console.clear()
        self.console.print("\n[bold cyan]Download File[/bold cyan]\n")
        
        try:
            profiles = self.config_mgr.list_profiles()
            
            if not profiles:
                self.console.print("[yellow]No profiles found.[/yellow]\n")
                Prompt.ask("Press Enter to continue")
                return
            
            # Select profile
            values = [(p['name'], f"{p['name']} ({p['host']})") for p in profiles]
            values.append(("cancel", "← Cancel"))
            
            profile_name = radiolist_dialog(
                title="",
                text="Select source:",
                values=values,
            ).run()
            
            if profile_name == "cancel" or not profile_name:
                return
            
            remote_path = Prompt.ask("[cyan]Remote file path[/cyan]")
            local_path = Prompt.ask("[cyan]Local destination path[/cyan]")
            
            self.console.print(f"\n[cyan]Downloading {remote_path}...[/cyan]\n")
            
            connection = self.conn_mgr.connect(profile_name)
            transfer = FileTransfer(connection.client)
            transfer.download(remote_path, local_path)
            
            self.console.print("[green]✓ Download completed![/green]\n")
            connection.disconnect()
            
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]\n")
        
        Prompt.ask("Press Enter to continue")
    
    # ===== SESSION MANAGEMENT =====
    
    def show_sessions(self):
        """Display active sessions."""
        self.console.clear()
        self.console.print("\n[bold cyan]Active Sessions[/bold cyan]\n")
        
        try:
            sessions = self.session_mgr.list_sessions()
            
            if not sessions:
                self.console.print("[yellow]No active sessions.[/yellow]\n")
            else:
                table = Table(show_header=True, header_style="bold cyan", box=None)
                table.add_column("ID", style="dim")
                table.add_column("Profile", style="cyan")
                table.add_column("Host", style="white")
                table.add_column("Status", style="green")
                table.add_column("Duration", style="dim")
                
                for session in sessions:
                    table.add_row(
                        session.get('id', 'N/A'),
                        session.get('profile', 'N/A'),
                        session.get('host', 'N/A'),
                        session.get('status', 'N/A'),
                        session.get('duration', 'N/A')
                    )
                
                self.console.print(table)
                self.console.print()
                
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]\n")
        
        Prompt.ask("Press Enter to continue")
    
    # ===== ADVANCED FEATURES =====
    
    def show_advanced(self):
        """Advanced features menu."""
        self.clear_screen()
        
        self.console.print()
        title = Text("Advanced Features", style="primary")
        self.console.print(Panel(title, border_style="border", padding=(0, 2)))
        self.console.print()
        
        result = radiolist_dialog(
            title="",
            text="Choose feature:",
            values=[
                ("local", "💻  Local Features (Laptop)"),
                ("remote", "🌐  Remote Features (Connected Device)"),
                ("monitoring", "📊  Connection Monitoring"),
                ("discovery", "🔍  Device Discovery"),
                ("security", "🔒  Security & Audit Logs"),
                ("automation", "⚡  Automation Scripts"),
                ("back", "⬅️  Back"),
            ],
            style=PT_DARK_STYLE,
        ).run()
        
        if result == "local":
            self.show_local_features_menu()
        elif result == "remote":
            self.show_remote_features_menu()
        elif result == "monitoring":
            self.show_monitoring()
        elif result == "discovery":
            self.show_discovery()
        elif result == "security":
            self.show_security()
        elif result == "automation":
            self.show_automation()
    
    def show_monitoring(self):
        """Connection monitoring dashboard."""
        self.console.clear()
        self.console.print("\n[bold cyan]Connection Monitoring[/bold cyan]\n")
        self.console.print("[yellow]Real-time monitoring coming soon![/yellow]\n")
        self.console.print("Features:")
        self.console.print("  • Connection health checks")
        self.console.print("  • Bandwidth monitoring")
        self.console.print("  • Latency tracking")
        self.console.print("  • Transfer statistics\n")
        Prompt.ask("Press Enter to continue")
    
    def show_discovery(self):
        """Device discovery on network."""
        self.console.clear()
        self.console.print("\n[bold cyan]Device Discovery[/bold cyan]\n")
        
        try:
            self.console.print("[cyan]Scanning network for SSH devices...[/cyan]\n")
            
            discovery = DeviceDiscovery()
            devices = discovery.scan()
            
            if not devices:
                self.console.print("[yellow]No devices found.[/yellow]\n")
            else:
                table = Table(show_header=True, header_style="bold cyan", box=None)
                table.add_column("IP Address", style="cyan")
                table.add_column("Port", style="white")
                table.add_column("Status", style="green")
                
                for device in devices:
                    table.add_row(
                        device.get('ip', 'N/A'),
                        str(device.get('port', 22)),
                        device.get('status', 'N/A')
                    )
                
                self.console.print(table)
                self.console.print()
                
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]\n")
        
        Prompt.ask("Press Enter to continue")
    
    def show_security(self):
        """Security and audit logs."""
        self.console.clear()
        self.console.print("\n[bold cyan]Security & Audit[/bold cyan]\n")
        self.console.print("[yellow]Audit log viewer coming soon![/yellow]\n")
        self.console.print("Features:")
        self.console.print("  • Connection attempt logs")
        self.console.print("  • File transfer history")
        self.console.print("  • Authentication failures")
        self.console.print("  • Security alerts\n")
        Prompt.ask("Press Enter to continue")
    
    def show_automation(self):
        """Automation scripts management."""
        self.console.clear()
        self.console.print("\n[bold cyan]Automation[/bold cyan]\n")
        self.console.print("[yellow]Automation features coming soon![/yellow]\n")
        self.console.print("Features:")
        self.console.print("  • Script scheduling")
        self.console.print("  • Batch operations")
        self.console.print("  • Automated backups")
        self.console.print("  • Task workflows\n")
        Prompt.ask("Press Enter to continue")
    
    # ===== LOCAL & REMOTE FEATURES =====
    
    def show_local_features_menu(self):
        """Display local (laptop) features menu."""
        self.clear_screen()
        
        self.console.print()
        title = Text("Local Features (Laptop)", style="primary")
        self.console.print(Panel(title, border_style="border", padding=(0, 2)))
        self.console.print()
        
        # Build menu from loaded local features
        values = []
        
        feature_icons = {
            "system_monitoring": "📊",
            "file_management": "📁",
            "network_tools": "🌐",
            "security_tools": "🔒",
            "automation": "⚙️"
        }
        
        for feature_name, feature_module in self.local_features.items():
            display_name = feature_name.replace('_', ' ').title()
            icon = feature_icons.get(feature_name, "🔧")
            values.append((feature_name, f"{icon}  {display_name}"))
        
        values.append(("back", "⬅️  Back to Advanced Menu"))
        
        result = radiolist_dialog(
            title="",
            text="Select a local feature to use:",
            values=values,
            style=PT_DARK_STYLE,
        ).run()
        
        if result and result != "back":
            self.execute_feature("local", result)
    
    def show_remote_features_menu(self):
        """Display remote (connected device) features menu."""
        self.clear_screen()
        
        self.console.print()
        title = Text("Remote Features (Connected Device)", style="primary")
        self.console.print(Panel(title, border_style="border", padding=(0, 2)))
        self.console.print()
        
        # Build menu from loaded remote features
        values = []
        
        feature_icons = {
            "remote_system_monitoring": "📊",
            "remote_file_management": "📁",
            "remote_process_management": "⚙️",
            "remote_network_tools": "🌐",
            "remote_security": "🔒"
        }
        
        for feature_name, feature_module in self.remote_features.items():
            display_name = feature_name.replace('_', ' ').title()
            icon = feature_icons.get(feature_name, "🔧")
            values.append((feature_name, f"{icon}  {display_name}"))
        
        values.append(("back", "⬅️  Back to Advanced Menu"))
        
        result = radiolist_dialog(
            title="",
            text="Select a remote feature to use:",
            values=values,
            style=PT_DARK_STYLE,
        ).run()
        
        if result and result != "back":
            self.execute_feature("remote", result)
    
    def execute_feature(self, feature_type, feature_name):
        """Execute a specific local or remote feature."""
        self.clear_screen()
        
        try:
            # Show loading animation
            with Progress(
                SpinnerColumn(spinner_name="dots"),
                TextColumn(f"[primary]Loading {feature_name.replace('_', ' ').title()}..."),
                transient=True,
                console=self.console
            ) as progress:
                progress.add_task("", total=None)
                time.sleep(0.5)
            
            # Get the appropriate feature module
            if feature_type == "local":
                feature_module = self.local_features.get(feature_name)
            else:
                feature_module = self.remote_features.get(feature_name)
            
            if feature_module and hasattr(feature_module, 'run'):
                # Execute the feature's run function
                self.console.print()
                feature_module.run()
            else:
                self.console.print(f"[error]✗ Feature '{feature_name}' not available or missing run() function[/error]\n")
                Prompt.ask("[dim]Press Enter to continue[/dim]")
        
        except Exception as e:
            self.console.print(f"[error]✗ Error executing feature: {e}[/error]\n")
            Prompt.ask("[dim]Press Enter to continue[/dim]")
    
    # ===== APPLICATION CONTROL =====
    
    def exit_application(self):
        """Exit the application with smooth fade-out effect."""
        self.clear_screen()
        
        # Animated goodbye message
        self.console.print("\n")
        with Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[primary]Closing..."),
            transient=True,
            console=self.console
        ) as progress:
            progress.add_task("", total=None)
            time.sleep(0.5)
        
        # Final message
        goodbye = Text()
        goodbye.append("✨ ", style="primary")
        goodbye.append("Goodbye!", style="info")
        goodbye.append(" ✨", style="primary")
        
        self.console.print(Panel(
            Align.center(goodbye),
            border_style="border",
            padding=(1, 4)
        ))
        self.console.print()
        
        time.sleep(0.3)  # Brief pause before exit
        self.running = False
        sys.exit(0)


def main():
    """Entry point for TUI Engine."""
    engine = TUIEngine()
    engine.run()


if __name__ == '__main__':
    main()
