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
                ("server_actions", "🖥️   Server Actions"),
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
        elif choice == "server_actions":
            self.show_server_actions()
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
        """Establish SSH connection and open device management menu."""
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
                "[success]✓ Connected successfully![/success]\n\n"
                f"[info]Profile:[/info] {profile_name}",
                border_style="success",
                padding=(1, 2)
            ))
            time.sleep(0.5)
            
            # Open device management session
            self.device_management_session(profile_name, session)
            
        except Exception as e:
            self.console.print()
            self.console.print(Panel(
                f"[error]✗ Connection failed[/error]\n\n[dim]{e}[/dim]",
                border_style="error",
                padding=(1, 2)
            ))
            self.console.print()
            Prompt.ask("[dim]Press Enter to continue[/dim]")
    
    def device_management_session(self, profile_name: str, session):
        """Interactive device management session with access to all remote features."""
        while True:
            self.clear_screen()
            
            self.console.print()
            title = Text(f"Device Session: {profile_name}", style="primary")
            self.console.print(Panel(title, border_style="border", padding=(0, 2)))
            self.console.print()
            
            result = radiolist_dialog(
                title="",
                text="What would you like to do?",
                values=[
                    ("remote_features", "🌐  Remote Device Features"),
                    ("file_transfer", "📁  File Transfer"),
                    ("shell", "💻  Interactive Shell"),
                    ("monitoring", "📊  Real-time Monitoring"),
                    ("disconnect", "🚪  Disconnect"),
                ],
                style=PT_DARK_STYLE,
            ).run()
            
            if result == "remote_features":
                self.show_remote_features_for_session(session)
            elif result == "file_transfer":
                self.show_transfer()
            elif result == "shell":
                self.console.print("\n[yellow]Interactive shell coming soon![/yellow]\n")
                self.console.print("[info]Will provide full terminal access to remote device[/info]\n")
                Prompt.ask("[dim]Press Enter to continue[/dim]")
            elif result == "monitoring":
                self.console.print("\n[yellow]Real-time monitoring coming soon![/yellow]\n")
                self.console.print("[info]Will show live system stats and logs[/info]\n")
                Prompt.ask("[dim]Press Enter to continue[/dim]")
            elif result == "disconnect" or result is None:
                # Disconnect from device
                try:
                    session.disconnect()
                    self.console.print("\n[success]✓ Disconnected from device[/success]\n")
                except:
                    pass
                time.sleep(0.3)
                break
    
    def show_remote_features_for_session(self, session):
        """Show remote features menu during an active session."""
        self.clear_screen()
        
        self.console.print()
        title = Text("Remote Device Features", style="primary")
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
        
        values.append(("back", "⬅️  Back to Session Menu"))
        
        result = radiolist_dialog(
            title="",
            text="Select a remote feature:",
            values=values,
            style=PT_DARK_STYLE,
        ).run()
        
        if result and result != "back":
            self.execute_feature("remote", result)
    
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
                        ("manager", "🎛️   Profile Manager (Advanced)"),
                        ("add", "➕  Add New Profile"),
                        ("edit", "✏️   Edit Profile"),
                        ("delete", "🗑️   Delete Profile"),
                        ("validate", "✅  Validate Connection"),
                        ("health", "🏥  Health Check"),
                        ("export", "📤  Export Profile"),
                        ("import", "📥  Import Profile"),
                        ("back", "⬅️  Back"),
                    ],
                    style=PT_DARK_STYLE,
                ).run()
                
                if result == "manager":
                    self.launch_profile_manager()
                elif result == "add":
                    self.add_profile()
                elif result == "edit":
                    self.edit_profile()
                elif result == "delete":
                    self.delete_profile()
                elif result == "validate":
                    self.validate_profile()
                elif result == "health":
                    self.check_profile_health()
                elif result == "export":
                    self.export_profile()
                elif result == "import":
                    self.import_profile()
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
    
    def launch_profile_manager(self):
        """Launch advanced Profile Manager with LOCAL/REMOTE routing."""
        try:
            from features.profile_manager import run_profile_manager
            run_profile_manager(self.config_mgr, self.conn_mgr)
        except Exception as e:
            self.console.print(f"[red]Error launching profile manager: {e}[/red]\n")
            import traceback
            traceback.print_exc()
            Prompt.ask("Press Enter to continue")
    
    def validate_profile(self):
        """Validate profile connection using REMOTE libraries."""
        self.console.clear()
        self.console.print("\n[bold cyan]Validate Profile Connection[/bold cyan]\n")
        
        profiles = self.config_mgr.list_profiles()
        if not profiles:
            self.console.print("[yellow]No profiles available.[/yellow]\n")
            Prompt.ask("Press Enter to continue")
            return
        
        values = [(p['name'], f"✅  {p['name']}") for p in profiles]
        values.append(("cancel", "❌  Cancel"))
        
        result = radiolist_dialog(
            title="",
            text="Select profile to validate:",
            values=values,
            style=PT_DARK_STYLE,
        ).run()
        
        if result and result != "cancel":
            try:
                from features.profile_manager import ProfileManager
                pm = ProfileManager(self.config_mgr, self.conn_mgr)
                pm.validate_profile_connection(result)
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]\n")
        
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
    
    def check_profile_health(self):
        """Run comprehensive health check on profile."""
        self.console.clear()
        self.console.print("\n[bold cyan]Profile Health Check[/bold cyan]\n")
        
        profiles = self.config_mgr.list_profiles()
        if not profiles:
            self.console.print("[yellow]No profiles available.[/yellow]\n")
            Prompt.ask("Press Enter to continue")
            return
        
        values = [(p['name'], f"🏥  {p['name']}") for p in profiles]
        values.append(("cancel", "❌  Cancel"))
        
        result = radiolist_dialog(
            title="",
            text="Select profile to check:",
            values=values,
            style=PT_DARK_STYLE,
        ).run()
        
        if result and result != "cancel":
            try:
                from features.profile_manager import ProfileManager
                pm = ProfileManager(self.config_mgr, self.conn_mgr)
                pm.check_profile_health(result)
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]\n")
                import traceback
                traceback.print_exc()
        
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
    
    def export_profile(self):
        """Export profile to file."""
        self.console.clear()
        self.console.print("\n[bold cyan]Export Profile[/bold cyan]\n")
        
        profiles = self.config_mgr.list_profiles()
        if not profiles:
            self.console.print("[yellow]No profiles available.[/yellow]\n")
            Prompt.ask("Press Enter to continue")
            return
        
        values = [(p['name'], f"�  {p['name']}") for p in profiles]
        values.append(("cancel", "❌  Cancel"))
        
        result = radiolist_dialog(
            title="",
            text="Select profile to export:",
            values=values,
            style=PT_DARK_STYLE,
        ).run()
        
        if result and result != "cancel":
            try:
                from features.profile_manager import ProfileManager
                pm = ProfileManager(self.config_mgr, self.conn_mgr)
                export_result = pm.export_profile(result)
                
                if export_result['success']:
                    self.console.print(f"\n[green]✓ Profile exported successfully![/green]")
                    self.console.print(f"[info]Location: {export_result['export_path']}[/info]\n")
                else:
                    self.console.print(f"\n[red]✗ Export failed: {export_result['error']}[/red]\n")
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]\n")
        
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
    
    def import_profile(self):
        """Import profile from file."""
        self.console.clear()
        self.console.print("\n[bold cyan]Import Profile[/bold cyan]\n")
        
        import_path = Prompt.ask("[cyan]Enter path to profile file[/cyan]")
        
        if not import_path:
            self.console.print("[yellow]Import cancelled.[/yellow]\n")
            Prompt.ask("Press Enter to continue")
            return
        
        try:
            from features.profile_manager import ProfileManager
            pm = ProfileManager(self.config_mgr, self.conn_mgr)
            result = pm.import_profile(import_path)
            
            if not result['success']:
                self.console.print(f"\n[red]✗ Import failed: {result['error']}[/red]\n")
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]\n")
        
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
    
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
        
        Prompt.ask("Press Enter to continue")    # ===== SETUP & CONFIGURATION =====
    
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
                ("auto_desktop", "🖥️   Desktop Server Setup (Run on Desktop)"),
                ("auto_laptop", "💻  Laptop Client Import (Run on Laptop)"),
                ("auto", "🤖  Legacy Auto Setup"),
                ("manual", "✍️   Manual Configuration"),
                ("import", "📥  Import SSH Config"),
                ("server", "🖥️   SSH Server Config"),
                ("back", "⬅️  Back"),
            ],
            style=PT_DARK_STYLE,
        ).run()
        
        if result == "auto_desktop":
            self.run_automated_desktop_setup()
        elif result == "auto_laptop":
            self.run_automated_laptop_import()
        elif result == "auto":
            self.run_auto_setup()
        elif result == "manual":
            self.add_profile()
        elif result == "import":
            self.import_ssh_config()
        elif result == "server":
            self.setup_ssh_server()
    
    def run_automated_desktop_setup(self):
        """Run automated desktop server setup using LOCAL libraries."""
        self.clear_screen()
        try:
            from features.automated_pairing import AutomatedPairing
            
            self.console.print("\n[bold cyan]Automated Desktop Server Setup[/bold cyan]\n")
            self.console.print("[info]This will configure this device as an SSH server using LOCAL system tools.[/info]\n")
            
            confirm = Prompt.ask("[yellow]Proceed with desktop setup?[/yellow] (y/n)", default="y")
            if confirm.lower() != 'y':
                return
            
            pairing = AutomatedPairing(self.config_mgr)
            result = pairing.setup_desktop_server()
            
            if result.get('success'):
                pairing.display_summary(result)
            else:
                self.console.print(f"[red]✗ Setup failed: {result.get('error')}[/red]\n")
                
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]\n")
            import traceback
            traceback.print_exc()
        
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
    
    def run_automated_laptop_import(self):
        """Run automated laptop client import using LOCAL libraries."""
        self.clear_screen()
        try:
            from features.automated_pairing import AutomatedPairing
            
            self.console.print("\n[bold cyan]Automated Laptop Client Import[/bold cyan]\n")
            self.console.print("[info]This will import a profile from your desktop using LOCAL client tools.[/info]\n")
            
            package_path = Prompt.ask("[cyan]Enter path to transfer package[/cyan]")
            
            if not package_path:
                self.console.print("[yellow]Import cancelled.[/yellow]\n")
                return
            
            pairing = AutomatedPairing(self.config_mgr)
            result = pairing.import_on_laptop(package_path)
            
            if result.get('success'):
                self.console.print("\n[green]✓ Import successful![/green]\n")
                
                # Offer to verify connection
                verify = Prompt.ask("[yellow]Verify connection now?[/yellow] (y/n)", default="y")
                if verify.lower() == 'y':
                    verify_result = pairing.verify_connection(
                        result['profile']['name'],
                        self.conn_mgr
                    )
                    
                    if verify_result.get('success'):
                        self.console.print("[green]✓ Connection verified![/green]\n")
                    else:
                        self.console.print(f"[yellow]⚠️  Verification issue: {verify_result.get('error')}[/yellow]\n")
            else:
                self.console.print(f"[red]✗ Import failed: {result.get('error')}[/red]\n")
                
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]\n")
            import traceback
            traceback.print_exc()
        
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
    
    def run_auto_setup(self):
        """Run legacy automated device setup."""
        try:
            self.console.print("\n[cyan]Starting legacy auto-setup...[/cyan]\n")
            
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
        """File transfer operations - redirect to local file_transfer feature."""
        # Use the dedicated file_transfer module from local features
        if "file_transfer" in self.local_features:
            feature_module = self.local_features.get("file_transfer")
            if feature_module and hasattr(feature_module, 'run'):
                try:
                    feature_module.run()
                except Exception as e:
                    self.console.print(f"[error]✗ Error in file transfer: {e}[/error]\n")
                    Prompt.ask("[dim]Press Enter to continue[/dim]")
            else:
                self.console.print("[error]✗ File transfer module not properly configured[/error]\n")
                Prompt.ask("[dim]Press Enter to continue[/dim]")
        else:
            # Fallback if module not loaded
            self.console.print("[error]✗ File transfer feature not available[/error]\n")
            Prompt.ask("[dim]Press Enter to continue[/dim]")
    
    # ===== SERVER ACTIONS =====
    
    def show_server_actions(self):
        """Remote server actions - manage SSH/SSHD server on remote desktop."""
        self.console.clear()
        self.console.print("\n[bold cyan]Server Actions[/bold cyan]\n")
        
        # Check if we have an active connection
        connections = self.conn_mgr.list_connections() if self.conn_mgr else []
        active_connections = [conn for conn in connections if conn.get('connected')]
        
        if not self.conn_mgr or not active_connections:
            self.console.print(Panel(
                "[yellow]⚠️  No active connection[/yellow]\n\n"
                "[info]Please connect to a device first:\n"
                "  1. Go to 'Connect to Device' from main menu\n"
                "  2. Select or create a connection\n"
                "  3. Return here to manage the remote server[/info]",
                border_style="yellow",
                padding=(1, 2)
            ))
            self.console.print()
            Prompt.ask("[dim]Press Enter to continue[/dim]")
            return
        
        # Use the remote_server_actions module
        if "remote_server_actions" in self.remote_features:
            feature_module = self.remote_features.get("remote_server_actions")
            if feature_module and hasattr(feature_module, 'run'):
                try:
                    feature_module.run(self.conn_mgr)
                except Exception as e:
                    self.console.print(f"[error]✗ Error in server actions: {e}[/error]\n")
                    Prompt.ask("[dim]Press Enter to continue[/dim]")
            else:
                self.console.print("[error]✗ Server actions module not properly configured[/error]\n")
                Prompt.ask("[dim]Press Enter to continue[/dim]")
        else:
            # Fallback if module not loaded
            self.console.print("[error]✗ Server actions feature not available[/error]\n")
            self.console.print("[info]Module should be at: personal-ssh-cli/remote/remote_server_actions.py[/info]\n")
            Prompt.ask("[dim]Press Enter to continue[/dim]")

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
            
            discovery = DeviceDiscovery(self.config_mgr)
            devices = discovery.scan_network()
            
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
            "file_transfer": "📤",
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
