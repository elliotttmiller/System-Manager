"""
Local File Management Module
Advanced file operations, search, and management on local system
"""

import os
import shutil
import hashlib
import mimetypes
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.tree import Tree
import json

console = Console()


class LocalFileManager:
    """Comprehensive local file management system"""
    
    def __init__(self):
        self.console = console
    
    def get_file_info(self, file_path):
        """Get detailed file information"""
        path = Path(file_path)
        
        if not path.exists():
            return {"error": "File does not exist"}
        
        stat = path.stat()
        
        return {
            "Name": path.name,
            "Path": str(path.absolute()),
            "Type": "Directory" if path.is_dir() else "File",
            "Size": f"{stat.st_size / 1024:.2f} KB" if stat.st_size < 1024*1024 else f"{stat.st_size / (1024**2):.2f} MB",
            "Created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "Modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "Accessed": datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d %H:%M:%S"),
            "Permissions": oct(stat.st_mode)[-3:],
            "MIME Type": mimetypes.guess_type(str(path))[0] or "Unknown"
        }
    
    def calculate_checksum(self, file_path, algorithm='sha256'):
        """Calculate file checksum"""
        hash_func = getattr(hashlib, algorithm)()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def search_files(self, directory, pattern="*", recursive=True):
        """Search for files matching pattern"""
        path = Path(directory)
        results = []
        
        try:
            if recursive:
                files = path.rglob(pattern)
            else:
                files = path.glob(pattern)
            
            for file in files:
                results.append({
                    "Path": str(file.absolute()),
                    "Name": file.name,
                    "Size": file.stat().st_size,
                    "Modified": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
        except Exception as e:
            return {"error": str(e)}
        
        return results
    
    def find_duplicates(self, directory):
        """Find duplicate files based on content hash"""
        hash_dict = {}
        duplicates = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_hash = self.calculate_checksum(file_path)
                    
                    if file_hash in hash_dict:
                        duplicates.append({
                            "Original": hash_dict[file_hash],
                            "Duplicate": file_path,
                            "Hash": file_hash
                        })
                    else:
                        hash_dict[file_hash] = file_path
                except Exception:
                    continue
        
        return duplicates
    
    def get_directory_size(self, directory):
        """Calculate total directory size"""
        total_size = 0
        
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except Exception:
                        continue
        except Exception as e:
            return {"error": str(e)}
        
        return total_size
    
    def organize_files(self, directory, organize_by='extension'):
        """Organize files in directory by type or date"""
        path = Path(directory)
        organized = {}
        
        try:
            for file in path.iterdir():
                if file.is_file():
                    if organize_by == 'extension':
                        key = file.suffix or 'no_extension'
                    elif organize_by == 'date':
                        key = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d")
                    else:
                        key = 'unknown'
                    
                    if key not in organized:
                        organized[key] = []
                    organized[key].append(str(file))
        except Exception as e:
            return {"error": str(e)}
        
        return organized
    
    def create_backup(self, source, destination):
        """Create backup of file or directory"""
        try:
            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
            return {"status": "success", "message": f"Backup created at {destination}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def batch_rename(self, directory, pattern, replacement):
        """Batch rename files matching pattern"""
        renamed = []
        errors = []
        
        try:
            path = Path(directory)
            for file in path.iterdir():
                if file.is_file() and pattern in file.name:
                    new_name = file.name.replace(pattern, replacement)
                    new_path = file.parent / new_name
                    try:
                        file.rename(new_path)
                        renamed.append({"old": file.name, "new": new_name})
                    except Exception as e:
                        errors.append({"file": file.name, "error": str(e)})
        except Exception as e:
            return {"error": str(e)}
        
        return {"renamed": renamed, "errors": errors}
    
    def display_directory_tree(self, directory, max_depth=3):
        """Display directory structure as tree"""
        tree = Tree(f"📁 {directory}", style="bold cyan")
        
        def add_to_tree(path, parent_tree, depth=0):
            if depth >= max_depth:
                return
            
            try:
                items = sorted(Path(path).iterdir(), key=lambda x: (not x.is_dir(), x.name))
                for item in items:
                    if item.is_dir():
                        branch = parent_tree.add(f"📁 {item.name}", style="cyan")
                        add_to_tree(item, branch, depth + 1)
                    else:
                        size = item.stat().st_size
                        size_str = f"{size / 1024:.1f} KB" if size < 1024*1024 else f"{size / (1024**2):.1f} MB"
                        parent_tree.add(f"📄 {item.name} ({size_str})", style="green")
            except PermissionError:
                parent_tree.add("⚠️ Permission Denied", style="red")
        
        add_to_tree(directory, tree)
        self.console.print(tree)
    
    def analyze_storage(self, directory):
        """Analyze storage usage by file types"""
        storage_by_type = {}
        total_size = 0
        
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    total_size += size
                    
                    ext = Path(file).suffix or 'no_extension'
                    storage_by_type[ext] = storage_by_type.get(ext, 0) + size
                except Exception:
                    continue
        
        return {
            "total_size": total_size,
            "by_type": storage_by_type
        }


def run():
    """Main entry point for local file management"""
    manager = LocalFileManager()
    
    console.print(Panel.fit(
        "[bold cyan]Local File Management[/bold cyan]\n"
        "Advanced file operations and management",
        border_style="cyan"
    ))
    
    options = [
        "1. Get File Information",
        "2. Search Files",
        "3. Find Duplicate Files",
        "4. Calculate Directory Size",
        "5. Organize Files",
        "6. Display Directory Tree",
        "7. Analyze Storage Usage",
        "8. Calculate File Checksum",
        "9. Create Backup",
        "10. Batch Rename Files",
        "0. Back to Main Menu"
    ]
    
    for option in options:
        console.print(f"  {option}")
    
    choice = console.input("\n[bold yellow]Enter your choice: [/bold yellow]")
    
    if choice == "1":
        file_path = console.input("[bold cyan]Enter file path: [/bold cyan]")
        info = manager.get_file_info(file_path)
        
        table = Table(title="File Information", style="cyan")
        table.add_column("Property", style="bold yellow")
        table.add_column("Value", style="green")
        
        for key, value in info.items():
            table.add_row(key, str(value))
        
        console.print(table)
    
    elif choice == "2":
        directory = console.input("[bold cyan]Enter directory to search: [/bold cyan]")
        pattern = console.input("[bold cyan]Enter search pattern (e.g., *.txt): [/bold cyan]")
        results = manager.search_files(directory, pattern)
        
        if isinstance(results, dict) and "error" in results:
            console.print(f"[red]Error: {results['error']}[/red]")
        else:
            table = Table(title=f"Search Results ({len(results)} files)", style="cyan")
            table.add_column("Name", style="bold yellow")
            table.add_column("Path", style="cyan")
            table.add_column("Size", style="green")
            table.add_column("Modified", style="magenta")
            
            for result in results[:50]:  # Limit to 50 results
                size = result['Size']
                size_str = f"{size / 1024:.2f} KB" if size < 1024*1024 else f"{size / (1024**2):.2f} MB"
                table.add_row(result['Name'], result['Path'], size_str, result['Modified'])
            
            console.print(table)
            if len(results) > 50:
                console.print(f"[yellow]Showing first 50 of {len(results)} results[/yellow]")
    
    elif choice == "3":
        directory = console.input("[bold cyan]Enter directory to scan for duplicates: [/bold cyan]")
        console.print("[yellow]Scanning for duplicates... This may take a while.[/yellow]")
        duplicates = manager.find_duplicates(directory)
        
        if duplicates:
            table = Table(title=f"Duplicate Files Found ({len(duplicates)})", style="cyan")
            table.add_column("Original", style="green")
            table.add_column("Duplicate", style="red")
            table.add_column("Hash", style="yellow")
            
            for dup in duplicates:
                table.add_row(dup['Original'], dup['Duplicate'], dup['Hash'][:16] + "...")
            
            console.print(table)
        else:
            console.print("[green]No duplicate files found![/green]")
    
    elif choice == "4":
        directory = console.input("[bold cyan]Enter directory path: [/bold cyan]")
        size = manager.get_directory_size(directory)
        
        if isinstance(size, dict) and "error" in size:
            console.print(f"[red]Error: {size['error']}[/red]")
        else:
            size_gb = size / (1024**3)
            size_mb = size / (1024**2)
            console.print(Panel.fit(
                f"[bold cyan]Directory Size:[/bold cyan]\n"
                f"Total: {size_gb:.2f} GB ({size_mb:.2f} MB)",
                border_style="cyan"
            ))
    
    elif choice == "6":
        directory = console.input("[bold cyan]Enter directory path: [/bold cyan]")
        depth = console.input("[bold cyan]Enter max depth (default 3): [/bold cyan]") or "3"
        manager.display_directory_tree(directory, int(depth))
    
    elif choice == "7":
        directory = console.input("[bold cyan]Enter directory to analyze: [/bold cyan]")
        console.print("[yellow]Analyzing storage... This may take a while.[/yellow]")
        analysis = manager.analyze_storage(directory)
        
        table = Table(title="Storage Analysis", style="cyan")
        table.add_column("File Type", style="bold yellow")
        table.add_column("Size", style="green")
        table.add_column("Percentage", style="magenta")
        
        total = analysis['total_size']
        sorted_types = sorted(analysis['by_type'].items(), key=lambda x: x[1], reverse=True)
        
        for ext, size in sorted_types[:20]:  # Top 20 types
            size_mb = size / (1024**2)
            percentage = (size / total * 100) if total > 0 else 0
            table.add_row(ext, f"{size_mb:.2f} MB", f"{percentage:.1f}%")
        
        console.print(table)
        console.print(f"\n[bold cyan]Total Size:[/bold cyan] {total / (1024**3):.2f} GB")
    
    elif choice == "8":
        file_path = console.input("[bold cyan]Enter file path: [/bold cyan]")
        algorithm = console.input("[bold cyan]Enter algorithm (md5/sha1/sha256, default sha256): [/bold cyan]") or "sha256"
        checksum = manager.calculate_checksum(file_path, algorithm)
        console.print(Panel.fit(
            f"[bold cyan]{algorithm.upper()} Checksum:[/bold cyan]\n{checksum}",
            border_style="cyan"
        ))
    
    console.input("\n[bold yellow]Press Enter to continue...[/bold yellow]")


if __name__ == "__main__":
    run()
