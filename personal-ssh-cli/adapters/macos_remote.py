"""
macOS Remote Device Adapter

macOS-specific remote device handling.
"""
from typing import Dict, Any


class MacOSRemoteAdapter:
    """Adapter for macOS remote devices."""
    
    def __init__(self, connection):
        """Initialize macOS adapter.
        
        Args:
            connection: SSHConnection instance
        """
        self.connection = connection
        self.os_info = None
    
    def detect_os(self) -> Dict[str, str]:
        """Detect macOS version.
        
        Returns:
            OS information dictionary
        """
        if self.os_info:
            return self.os_info
        
        try:
            result = self.connection.execute_command('sw_vers')
            
            if result['exit_code'] == 0:
                os_info = self._parse_sw_vers(result['stdout'])
                self.os_info = os_info
                return os_info
        except Exception:
            pass
        
        self.os_info = {
            'name': 'macOS',
            'version': 'Unknown',
        }
        return self.os_info
    
    def _parse_sw_vers(self, content: str) -> Dict[str, str]:
        """Parse sw_vers output.
        
        Args:
            content: Command output
            
        Returns:
            Parsed information
        """
        info = {}
        for line in content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip()] = value.strip()
        
        return {
            'name': info.get('ProductName', 'macOS'),
            'version': info.get('ProductVersion', 'Unknown'),
            'build': info.get('BuildVersion', 'Unknown'),
        }
    
    def get_homebrew_installed(self) -> bool:
        """Check if Homebrew is installed.
        
        Returns:
            True if Homebrew is available
        """
        result = self.connection.execute_command('which brew')
        return result['exit_code'] == 0
    
    def install_homebrew_package(self, package_name: str) -> bool:
        """Install package using Homebrew.
        
        Args:
            package_name: Package to install
            
        Returns:
            True if installation successful
        """
        if not self.get_homebrew_installed():
            return False
        
        result = self.connection.execute_command(f'brew install {package_name}')
        return result['exit_code'] == 0
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information.
        
        Returns:
            System information dictionary
        """
        info = {
            'os': self.detect_os(),
            'homebrew_installed': self.get_homebrew_installed(),
        }
        
        # Get hardware info
        result = self.connection.execute_command('sysctl -n machdep.cpu.brand_string')
        if result['exit_code'] == 0:
            info['cpu'] = result['stdout'].strip()
        
        # Get uptime
        result = self.connection.execute_command('uptime')
        if result['exit_code'] == 0:
            info['uptime'] = result['stdout'].strip()
        
        return info
    
    def normalize_path(self, path: str) -> str:
        """Normalize macOS path.
        
        Args:
            path: File path
            
        Returns:
            Normalized path
        """
        # macOS uses POSIX paths
        return path.replace('\\', '/')
