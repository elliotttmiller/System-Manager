"""
Terminal UI Components

Rich terminal rendering and interactions.
"""
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from typing import Optional, Callable


class TerminalUI:
    """Terminal user interface utilities."""
    
    def __init__(self):
        """Initialize terminal UI."""
        self.console = Console()
    
    def print(self, message: str, style: Optional[str] = None):
        """Print message to console.
        
        Args:
            message: Message to print
            style: Optional Rich style string
        """
        if style:
            self.console.print(f"[{style}]{message}[/{style}]")
        else:
            self.console.print(message)
    
    def print_success(self, message: str):
        """Print success message."""
        self.console.print(f"[green]✓ {message}[/green]")
    
    def print_error(self, message: str):
        """Print error message."""
        self.console.print(f"[red]✗ {message}[/red]")
    
    def print_warning(self, message: str):
        """Print warning message."""
        self.console.print(f"[yellow]⚠ {message}[/yellow]")
    
    def print_info(self, message: str):
        """Print info message."""
        self.console.print(f"[blue]ℹ {message}[/blue]")
    
    def create_table(self, title: str, columns: list) -> Table:
        """Create a Rich table.
        
        Args:
            title: Table title
            columns: List of tuples (name, style)
            
        Returns:
            Rich Table instance
        """
        table = Table(title=title)
        
        for col_name, col_style in columns:
            table.add_column(col_name, style=col_style)
        
        return table
    
    def print_table(self, table: Table):
        """Print table to console.
        
        Args:
            table: Rich Table to print
        """
        self.console.print(table)
    
    def create_panel(self, content: str, title: Optional[str] = None,
                    style: str = "blue") -> Panel:
        """Create a Rich panel.
        
        Args:
            content: Panel content
            title: Optional panel title
            style: Panel border style
            
        Returns:
            Rich Panel instance
        """
        return Panel(content, title=title, border_style=style)
    
    def print_panel(self, content: str, title: Optional[str] = None,
                   style: str = "blue"):
        """Print panel to console.
        
        Args:
            content: Panel content
            title: Optional panel title
            style: Panel border style
        """
        panel = self.create_panel(content, title, style)
        self.console.print(panel)
    
    def print_code(self, code: str, language: str = "python",
                  theme: str = "monokai"):
        """Print syntax-highlighted code.
        
        Args:
            code: Code to display
            language: Programming language
            theme: Syntax highlighting theme
        """
        syntax = Syntax(code, language, theme=theme)
        self.console.print(syntax)
    
    def print_markdown(self, markdown_text: str):
        """Print markdown content.
        
        Args:
            markdown_text: Markdown content
        """
        md = Markdown(markdown_text)
        self.console.print(md)
    
    def create_progress(self) -> Progress:
        """Create progress bar for file transfers.
        
        Returns:
            Rich Progress instance
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            console=self.console
        )
    
    def confirm(self, message: str, default: bool = True) -> bool:
        """Ask user for confirmation.
        
        Args:
            message: Confirmation message
            default: Default choice
            
        Returns:
            True if confirmed
        """
        suffix = " [Y/n]" if default else " [y/N]"
        response = self.console.input(f"[yellow]{message}{suffix}[/yellow] ")
        
        if not response:
            return default
        
        return response.lower() in ['y', 'yes']
    
    def prompt(self, message: str, password: bool = False) -> str:
        """Prompt user for input.
        
        Args:
            message: Prompt message
            password: Hide input for passwords
            
        Returns:
            User input
        """
        if password:
            import getpass
            return getpass.getpass(f"{message}: ")
        else:
            return self.console.input(f"[cyan]{message}:[/cyan] ")
    
    def clear_screen(self):
        """Clear the terminal screen."""
        self.console.clear()
    
    def print_separator(self, char: str = "─"):
        """Print separator line.
        
        Args:
            char: Character to use for separator
        """
        width = self.console.width
        self.console.print(char * width, style="dim")
