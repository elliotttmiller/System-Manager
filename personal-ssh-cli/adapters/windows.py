"""
Windows Platform Adapter

Windows-specific integrations and utilities.
"""
import platform
from typing import Optional, Dict, Any


class WindowsAdapter:
    """Windows platform adapter."""
    
    def __init__(self):
        """Initialize Windows adapter."""
        self.is_windows = platform.system() == "Windows"
    
    def normalize_path(self, path: str, to_posix: bool = False) -> str:
        """Normalize Windows path.
        
        Args:
            path: File path
            to_posix: Convert to POSIX format
            
        Returns:
            Normalized path
        """
        if to_posix:
            # Convert Windows path to POSIX
            return path.replace('\\', '/')
        else:
            # Convert POSIX path to Windows
            return path.replace('/', '\\')
    
    def get_credential_manager_password(self, target: str) -> Optional[str]:
        """Get password from Windows Credential Manager.
        
        Args:
            target: Credential target name
            
        Returns:
            Password or None
        """
        if not self.is_windows:
            return None
        
        try:
            import keyring
            return keyring.get_password("personal-ssh-cli", target)
        except Exception:
            return None
    
    def set_credential_manager_password(self, target: str, password: str) -> bool:
        """Store password in Windows Credential Manager.
        
        Args:
            target: Credential target name
            password: Password to store
            
        Returns:
            True if successful
        """
        if not self.is_windows:
            return False
        
        try:
            import keyring
            keyring.set_password("personal-ssh-cli", target, password)
            return True
        except Exception:
            return False
    
    def execute_powershell(self, script: str) -> Dict[str, Any]:
        """Execute PowerShell script.
        
        Args:
            script: PowerShell script to execute
            
        Returns:
            Execution result dictionary
        """
        if not self.is_windows:
            return {'success': False, 'error': 'Not on Windows'}
        
        import subprocess
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'exit_code': result.returncode,
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    def get_windows_terminal_available(self) -> bool:
        """Check if Windows Terminal is available.
        
        Returns:
            True if Windows Terminal is installed
        """
        if not self.is_windows:
            return False
        
        import shutil
        return shutil.which('wt') is not None
    
    def launch_windows_terminal(self, command: Optional[str] = None) -> bool:
        """Launch Windows Terminal.
        
        Args:
            command: Optional command to run in terminal
            
        Returns:
            True if launched successfully
        """
        if not self.get_windows_terminal_available():
            return False
        
        import subprocess
        
        try:
            cmd = ['wt']
            if command:
                cmd.extend(['-w', '0', 'nt', command])
            
            subprocess.Popen(cmd)
            return True
        except Exception:
            return False
