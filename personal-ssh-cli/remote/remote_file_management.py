"""
Remote File Management Module
File operations and management on remote devices via SSH
"""

import paramiko
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress
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


class RemoteFileManager:
    """Comprehensive remote file management via SSH"""
    
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
    
    def list_directory(self, path="/"):
        """List contents of remote directory"""
        cmd = f"ls -lah {path}"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Unknown error')}
    
    def get_file_info(self, file_path):
        """Get detailed information about a remote file"""
        cmd = f"stat {file_path}"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'File not found')}
    
    def create_directory(self, path):
        """Create directory on remote device"""
        cmd = f"mkdir -p {path}"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"status": "success", "message": f"Directory created: {path}"}
        else:
            return {"status": "error", "message": result.get('message', 'Failed to create directory')}
    
    def delete_file(self, path):
        """Delete file on remote device"""
        cmd = f"rm {path}"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"status": "success", "message": f"File deleted: {path}"}
        else:
            return {"status": "error", "message": result.get('message', 'Failed to delete file')}
    
    def delete_directory(self, path):
        """Delete directory on remote device"""
        cmd = f"rm -rf {path}"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"status": "success", "message": f"Directory deleted: {path}"}
        else:
            return {"status": "error", "message": result.get('message', 'Failed to delete directory')}
    
    def move_file(self, source, destination):
        """Move/rename file on remote device"""
        cmd = f"mv {source} {destination}"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"status": "success", "message": f"Moved {source} to {destination}"}
        else:
            return {"status": "error", "message": result.get('message', 'Failed to move file')}
    
    def copy_file(self, source, destination):
        """Copy file on remote device"""
        cmd = f"cp {source} {destination}"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"status": "success", "message": f"Copied {source} to {destination}"}
        else:
            return {"status": "error", "message": result.get('message', 'Failed to copy file')}
    
    def get_disk_usage(self, path="/"):
        """Get disk usage for path"""
        cmd = f"du -sh {path}"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Failed to get disk usage')}
    
    def search_files(self, path, pattern):
        """Search for files matching pattern"""
        cmd = f"find {path} -name '{pattern}'"
        result = self.execute_command(cmd)
        
        if result['status'] == "success":
            return {"output": result['output']}
        else:
            return {"error": result.get('message', 'Search failed')}
    
    def disconnect(self):
        """Close SSH connection"""
        if self.ssh_client:
            self.ssh_client.close()
            return {"status": "success", "message": "Disconnected"}
        return {"status": "error", "message": "Not connected"}


def run():
    """Main entry point for remote file management"""
    manager = RemoteFileManager()
    
    console.print(Panel.fit(
        "[bold cyan]Remote File Management[/bold cyan]\n"
        "Manage files on remote devices via SSH",
        border_style="cyan"
    ))
    
    # Get connection details
    host = console.input("[bold cyan]Enter remote host: [/bold cyan]")
    username = console.input("[bold cyan]Enter username: [/bold cyan]")
    auth_method = console.input("[bold cyan]Authentication method (password/key): [/bold cyan]")
    
    if auth_method.lower() == "password":
        from getpass import getpass
        password = getpass("Enter password: ")
        result = manager.connect(host, username, password=password)
    else:
        key_file = console.input("[bold cyan]Enter key file path: [/bold cyan]")
        result = manager.connect(host, username, key_filename=key_file)
    
    if result['status'] != "success":
        console.print(f"[red]Connection failed: {result['message']}[/red]")
        return
    
    console.print(f"[green]{result['message']}[/green]")
    
    while True:
        console.print()
        
        operation = radiolist_dialog(
            title="File Management",
            text="Select operation:",
            values=[
                ("list", "📋  List Directory"),
                ("info", "ℹ️  File Info"),
                ("create", "📁  Create Directory"),
                ("delete_file", "🗑️  Delete File"),
                ("delete_dir", "🗑️  Delete Directory"),
                ("move", "✂️  Move/Rename"),
                ("copy", "📄  Copy File"),
                ("search", "🔍  Search Files"),
                ("disk", "💾  Disk Usage"),
                ("exit", "❌  Exit"),
            ],
            style=PT_DARK_STYLE,
        ).run()
        
        if operation == "list":
            path = Prompt.ask("[cyan]Directory path[/cyan]", default="/")
            result = manager.list_directory(path)
            if 'output' in result:
                console.print(Panel(result['output'], title=f"Directory: {path}", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "info":
            file_path = Prompt.ask("[cyan]File path[/cyan]")
            result = manager.get_file_info(file_path)
            if 'output' in result:
                console.print(Panel(result['output'], title="File Information", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "create":
            path = Prompt.ask("[cyan]Directory path to create[/cyan]")
            result = manager.create_directory(path)
            if result['status'] == "success":
                console.print(f"[green]✓ {result['message']}[/green]")
            else:
                console.print(f"[red]✗ {result['message']}[/red]")
        
        elif operation == "delete_file":
            path = Prompt.ask("[cyan]File path to delete[/cyan]")
            if Confirm.ask(f"[yellow]Delete {path}?[/yellow]", default=False):
                result = manager.delete_file(path)
                if result['status'] == "success":
                    console.print(f"[green]✓ {result['message']}[/green]")
                else:
                    console.print(f"[red]✗ {result['message']}[/red]")
        
        elif operation == "delete_dir":
            path = Prompt.ask("[cyan]Directory path to delete[/cyan]")
            if Confirm.ask(f"[yellow]Delete directory {path} and all contents?[/yellow]", default=False):
                result = manager.delete_directory(path)
                if result['status'] == "success":
                    console.print(f"[green]✓ {result['message']}[/green]")
                else:
                    console.print(f"[red]✗ {result['message']}[/red]")
        
        elif operation == "move":
            source = Prompt.ask("[cyan]Source path[/cyan]")
            destination = Prompt.ask("[cyan]Destination path[/cyan]")
            result = manager.move_file(source, destination)
            if result['status'] == "success":
                console.print(f"[green]✓ {result['message']}[/green]")
            else:
                console.print(f"[red]✗ {result['message']}[/red]")
        
        elif operation == "copy":
            source = Prompt.ask("[cyan]Source path[/cyan]")
            destination = Prompt.ask("[cyan]Destination path[/cyan]")
            result = manager.copy_file(source, destination)
            if result['status'] == "success":
                console.print(f"[green]✓ {result['message']}[/green]")
            else:
                console.print(f"[red]✗ {result['message']}[/red]")
        
        elif operation == "search":
            path = Prompt.ask("[cyan]Search in directory[/cyan]", default="/")
            pattern = Prompt.ask("[cyan]File pattern[/cyan]", default="*")
            result = manager.search_files(path, pattern)
            if 'output' in result:
                console.print(Panel(result['output'], title="Search Results", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "disk":
            path = Prompt.ask("[cyan]Path to check[/cyan]", default="/")
            result = manager.get_disk_usage(path)
            if 'output' in result:
                console.print(Panel(result['output'], title="Disk Usage", border_style="cyan"))
            else:
                console.print(f"[red]Error: {result.get('error')}[/red]")
        
        elif operation == "exit" or operation is None:
            break
    
    manager.disconnect()
    console.print("[green]Disconnected from remote device[/green]")
    Prompt.ask("\nPress Enter to continue")


if __name__ == "__main__":
    run()
