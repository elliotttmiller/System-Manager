"""
Utility Functions

Helper functions and system utilities.
"""
import os
import platform
from pathlib import Path
from typing import Optional


def get_os_type() -> str:
    """Get operating system type.
    
    Returns:
        OS type string (windows, linux, macos)
    """
    system = platform.system().lower()
    
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    else:
        return "linux"


def is_windows() -> bool:
    """Check if running on Windows."""
    return get_os_type() == "windows"


def is_linux() -> bool:
    """Check if running on Linux."""
    return get_os_type() == "linux"


def is_macos() -> bool:
    """Check if running on macOS."""
    return get_os_type() == "macos"


def format_bytes(size: int) -> str:
    """Format bytes to human-readable string.
    
    Args:
        size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format duration to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "1h 23m 45s")
    """
    if seconds < 60:
        return f"{seconds:.0f}s"
    
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.0f}m"
    
    hours = minutes / 60
    if hours < 24:
        return f"{hours:.0f}h {minutes % 60:.0f}m"
    
    days = hours / 24
    return f"{days:.0f}d {hours % 24:.0f}h"


def normalize_path(path: str) -> str:
    """Normalize file path for current OS.
    
    Args:
        path: File path
        
    Returns:
        Normalized path
    """
    return str(Path(path).resolve())


def expand_user(path: str) -> str:
    """Expand user home directory in path.
    
    Args:
        path: File path
        
    Returns:
        Expanded path
    """
    return str(Path(path).expanduser())


def ensure_directory(path: str):
    """Ensure directory exists.
    
    Args:
        path: Directory path
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def get_terminal_size() -> tuple:
    """Get terminal size.
    
    Returns:
        Tuple of (width, height)
    """
    try:
        size = os.get_terminal_size()
        return (size.columns, size.lines)
    except Exception:
        return (80, 24)  # Default size


def validate_hostname(hostname: str) -> bool:
    """Validate hostname format.
    
    Args:
        hostname: Hostname to validate
        
    Returns:
        True if valid
    """
    import re
    # Simple hostname validation
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    return bool(re.match(pattern, hostname))


def validate_ip(ip: str) -> bool:
    """Validate IP address format.
    
    Args:
        ip: IP address to validate
        
    Returns:
        True if valid
    """
    import socket
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False
