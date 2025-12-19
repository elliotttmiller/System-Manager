"""
Local File Transfer Module
Comprehensive file transfer operations to/from remote devices via SSH/SCP
"""

import os
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn
from rich.prompt import Prompt, Confirm
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.styles import Style as PTStyle
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from core.config_manager import ConfigManager
    from core.connection_manager import ConnectionManager
    from core.file_transfer import FileTransfer
except:
    # Fallback for direct module execution
    pass

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


class LocalFileTransfer:
    """Comprehensive local file transfer operations to/from remote devices"""
    
    def __init__(self, config_dir=None):
        self.console = console
        self.config_dir = config_dir or Path.home() / ".ssh_manager"
        self.config_mgr = None
        self.conn_mgr = None
        
    def initialize_managers(self):
        """Initialize configuration and connection managers"""
        try:
            self.config_mgr = ConfigManager(self.config_dir)
            self.config_mgr.initialize()
            self.conn_mgr = ConnectionManager(self.config_mgr)
            return True
        except Exception as e:
            self.console.print(f"[red]Failed to initialize managers: {e}[/red]")
            return False
    
    def select_profile(self, action="transfer"):
        """Select a device profile for transfer operations"""
        try:
            profiles = self.config_mgr.list_profiles()
            
            if not profiles:
                self.console.print(Panel(
                    "[yellow]⚠️  No device profiles configured[/yellow]\n\n"
                    "[dim]Create a profile in Setup New Device first[/dim]",
                    border_style="yellow",
                    padding=(1, 2)
                ))
                return None
            
            # Build profile selection list
            values = []
            for profile in profiles:
                name = profile.get('name', 'Unknown')
                host = profile.get('host', 'N/A')
                user = profile.get('username', 'N/A')
                display = f"🖥️  {name}  [dim]→[/dim]  {user}@{host}"
                values.append((name, display))
            
            values.append(("cancel", "❌  Cancel"))
            
            result = radiolist_dialog(
                title="",
                text=f"Select device for {action}:",
                values=values,
                style=PT_DARK_STYLE,
            ).run()
            
            return result if result != "cancel" else None
            
        except Exception as e:
            self.console.print(f"[red]Error selecting profile: {e}[/red]")
            return None
    
    def upload_file(self):
        """Upload file to remote device"""
        self.console.clear()
        self.console.print()
        
        title = Panel("⬆️  Upload File to Remote Device", style="bold cyan", border_style="cyan")
        self.console.print(title)
        self.console.print()
        
        # Select destination device
        profile_name = self.select_profile("upload")
        if not profile_name:
            return
        
        # Get local file path
        self.console.print()
        local_path = Prompt.ask("[cyan]📄 Local file path[/cyan]")
        
        if not os.path.exists(local_path):
            self.console.print(f"\n[red]✗ File not found: {local_path}[/red]\n")
            Prompt.ask("[dim]Press Enter to continue[/dim]")
            return
        
        # Get remote destination
        remote_path = Prompt.ask("[cyan]📁 Remote destination path[/cyan]")
        
        # Confirm transfer
        file_size = os.path.getsize(local_path)
        size_mb = file_size / (1024 * 1024)
        
        self.console.print()
        self.console.print(Panel(
            f"[cyan]File:[/cyan] {os.path.basename(local_path)}\n"
            f"[cyan]Size:[/cyan] {size_mb:.2f} MB\n"
            f"[cyan]From:[/cyan] {local_path}\n"
            f"[cyan]To:[/cyan] {profile_name}:{remote_path}",
            title="Transfer Details",
            border_style="cyan"
        ))
        self.console.print()
        
        if not Confirm.ask("Proceed with upload?", default=True):
            self.console.print("[yellow]Upload cancelled[/yellow]\n")
            return
        
        # Perform upload with progress
        try:
            self.console.print()
            with Progress(
                SpinnerColumn(spinner_name="dots"),
                TextColumn("[cyan]{task.description}"),
                BarColumn(complete_style="green", finished_style="green"),
                TextColumn("[cyan]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Uploading {os.path.basename(local_path)}...", total=100)
                
                # Connect to device
                connection = self.conn_mgr.connect(profile_name)
                transfer = FileTransfer(connection.client)
                
                # Upload file
                transfer.upload(local_path, remote_path)
                
                # Simulate progress (in production, this would track actual transfer)
                for i in range(100):
                    progress.update(task, advance=1)
                
                connection.disconnect()
            
            self.console.print()
            self.console.print(Panel(
                "[green]✓ Upload completed successfully![/green]",
                border_style="green",
                padding=(0, 2)
            ))
            self.console.print()
            
        except Exception as e:
            self.console.print()
            self.console.print(Panel(
                f"[red]✗ Upload failed[/red]\n\n[dim]{str(e)}[/dim]",
                border_style="red",
                padding=(1, 2)
            ))
            self.console.print()
        
        Prompt.ask("[dim]Press Enter to continue[/dim]")
    
    def download_file(self):
        """Download file from remote device"""
        self.console.clear()
        self.console.print()
        
        title = Panel("⬇️  Download File from Remote Device", style="bold cyan", border_style="cyan")
        self.console.print(title)
        self.console.print()
        
        # Select source device
        profile_name = self.select_profile("download")
        if not profile_name:
            return
        
        # Get remote file path
        self.console.print()
        remote_path = Prompt.ask("[cyan]📄 Remote file path[/cyan]")
        
        # Get local destination
        local_path = Prompt.ask("[cyan]📁 Local destination path[/cyan]", default="./")
        
        # Perform download with progress
        try:
            self.console.print()
            with Progress(
                SpinnerColumn(spinner_name="dots"),
                TextColumn("[cyan]{task.description}"),
                BarColumn(complete_style="green", finished_style="green"),
                TextColumn("[cyan]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Downloading {os.path.basename(remote_path)}...", total=100)
                
                # Connect to device
                connection = self.conn_mgr.connect(profile_name)
                transfer = FileTransfer(connection.client)
                
                # Download file
                transfer.download(remote_path, local_path)
                
                # Simulate progress
                for i in range(100):
                    progress.update(task, advance=1)
                
                connection.disconnect()
            
            self.console.print()
            self.console.print(Panel(
                f"[green]✓ Download completed successfully![/green]\n\n"
                f"[cyan]Saved to:[/cyan] {os.path.abspath(local_path)}",
                border_style="green",
                padding=(1, 2)
            ))
            self.console.print()
            
        except Exception as e:
            self.console.print()
            self.console.print(Panel(
                f"[red]✗ Download failed[/red]\n\n[dim]{str(e)}[/dim]",
                border_style="red",
                padding=(1, 2)
            ))
            self.console.print()
        
        Prompt.ask("[dim]Press Enter to continue[/dim]")
    
    def sync_directory(self):
        """Synchronize directory with remote device"""
        self.console.clear()
        self.console.print()
        
        title = Panel("🔄  Sync Directory with Remote Device", style="bold cyan", border_style="cyan")
        self.console.print(title)
        self.console.print()
        
        # Select device
        profile_name = self.select_profile("sync")
        if not profile_name:
            return
        
        # Get sync direction
        direction_result = radiolist_dialog(
            title="Sync Direction",
            text="Choose sync direction:",
            values=[
                ("to_remote", "📤  Local → Remote (Upload)"),
                ("from_remote", "📥  Remote → Local (Download)"),
                ("bidirectional", "🔄  Bidirectional Sync"),
                ("cancel", "❌  Cancel"),
            ],
            style=PT_DARK_STYLE,
        ).run()
        
        if direction_result == "cancel" or not direction_result:
            return
        
        self.console.print()
        local_dir = Prompt.ask("[cyan]📁 Local directory path[/cyan]")
        remote_dir = Prompt.ask("[cyan]📁 Remote directory path[/cyan]")
        
        self.console.print()
        self.console.print(Panel(
            f"[yellow]⚠️  Directory sync feature coming soon![/yellow]\n\n"
            f"[cyan]Local:[/cyan] {local_dir}\n"
            f"[cyan]Remote:[/cyan] {profile_name}:{remote_dir}\n"
            f"[cyan]Direction:[/cyan] {direction_result}",
            border_style="yellow",
            padding=(1, 2)
        ))
        self.console.print()
        
        Prompt.ask("[dim]Press Enter to continue[/dim]")
    
    def batch_transfer(self):
        """Batch file transfer operations"""
        self.console.clear()
        self.console.print()
        
        title = Panel("📦  Batch File Transfer", style="bold cyan", border_style="cyan")
        self.console.print(title)
        self.console.print()
        
        self.console.print(Panel(
            "[yellow]⚠️  Batch transfer feature coming soon![/yellow]\n\n"
            "[dim]Features:[/dim]\n"
            "  • Upload multiple files at once\n"
            "  • Download multiple files at once\n"
            "  • Transfer with pattern matching\n"
            "  • Queue management",
            border_style="yellow",
            padding=(1, 2)
        ))
        self.console.print()
        
        Prompt.ask("[dim]Press Enter to continue[/dim]")
    
    def show_transfer_history(self):
        """Show file transfer history"""
        self.console.clear()
        self.console.print()
        
        title = Panel("📋  Transfer History", style="bold cyan", border_style="cyan")
        self.console.print(title)
        self.console.print()
        
        # This would load from a history file in production
        self.console.print(Panel(
            "[yellow]⚠️  Transfer history feature coming soon![/yellow]\n\n"
            "[dim]Will show:[/dim]\n"
            "  • Recent transfers\n"
            "  • Transfer status\n"
            "  • File sizes and times\n"
            "  • Success/failure logs",
            border_style="yellow",
            padding=(1, 2)
        ))
        self.console.print()
        
        Prompt.ask("[dim]Press Enter to continue[/dim]")


def run():
    """Main entry point for local file transfer"""
    transfer = LocalFileTransfer()
    
    # Initialize managers
    if not transfer.initialize_managers():
        console.print("\n[red]Failed to initialize. Please check configuration.[/red]\n")
        Prompt.ask("[dim]Press Enter to continue[/dim]")
        return
    
    while True:
        transfer.console.clear()
        transfer.console.print()
        
        title = Panel("📁  File Transfer Operations", style="bold cyan", border_style="cyan")
        transfer.console.print(title)
        transfer.console.print()
        
        # Show transfer menu
        result = radiolist_dialog(
            title="",
            text="Select transfer operation:",
            values=[
                ("upload", "⬆️  Upload File to Remote"),
                ("download", "⬇️  Download File from Remote"),
                ("sync", "🔄  Sync Directory"),
                ("batch", "📦  Batch Transfer"),
                ("history", "📋  Transfer History"),
                ("back", "⬅️  Back"),
            ],
            style=PT_DARK_STYLE,
        ).run()
        
        if result == "upload":
            transfer.upload_file()
        elif result == "download":
            transfer.download_file()
        elif result == "sync":
            transfer.sync_directory()
        elif result == "batch":
            transfer.batch_transfer()
        elif result == "history":
            transfer.show_transfer_history()
        elif result == "back" or result is None:
            break


if __name__ == "__main__":
    run()
