"""
Linux Remote Device Adapter

Linux-specific remote device handling.
"""
from typing import Dict, Any, Optional


class LinuxRemoteAdapter:
    """Adapter for Linux remote devices."""
    
    def __init__(self, connection):
        """Initialize Linux adapter.
        
        Args:
            connection: SSHConnection instance
        """
        self.connection = connection
        self.os_info = None
    
    def detect_os(self) -> Dict[str, str]:
        """Detect Linux distribution and version.
        
        Returns:
            OS information dictionary
        """
        if self.os_info:
            return self.os_info
        
        try:
            # Try to read /etc/os-release
            result = self.connection.execute_command('cat /etc/os-release')
            
            if result['exit_code'] == 0:
                os_info = self._parse_os_release(result['stdout'])
                self.os_info = os_info
                return os_info
        except Exception:
            pass
        
        # Fallback
        self.os_info = {
            'distribution': 'Linux',
            'version': 'Unknown',
        }
        return self.os_info
    
    def _parse_os_release(self, content: str) -> Dict[str, str]:
        """Parse /etc/os-release content.
        
        Args:
            content: File content
            
        Returns:
            Parsed information
        """
        info = {}
        for line in content.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                info[key] = value.strip('"')
        
        return {
            'distribution': info.get('NAME', 'Linux'),
            'version': info.get('VERSION', 'Unknown'),
            'id': info.get('ID', 'linux'),
        }
    
    def get_package_manager(self) -> str:
        """Detect package manager.
        
        Returns:
            Package manager name (apt, yum, dnf, pacman, etc.)
        """
        os_info = self.detect_os()
        os_id = os_info.get('id', '').lower()
        
        # Map distribution to package manager
        if os_id in ['ubuntu', 'debian']:
            return 'apt'
        elif os_id in ['fedora', 'rhel', 'centos']:
            return 'dnf' if self._command_exists('dnf') else 'yum'
        elif os_id == 'arch':
            return 'pacman'
        else:
            # Try to detect
            if self._command_exists('apt'):
                return 'apt'
            elif self._command_exists('dnf'):
                return 'dnf'
            elif self._command_exists('yum'):
                return 'yum'
            elif self._command_exists('pacman'):
                return 'pacman'
        
        return 'unknown'
    
    def _command_exists(self, command: str) -> bool:
        """Check if command exists on remote system.
        
        Args:
            command: Command name
            
        Returns:
            True if command exists
        """
        result = self.connection.execute_command(f'which {command}')
        return result['exit_code'] == 0
    
    def install_package(self, package_name: str) -> bool:
        """Install package using detected package manager.
        
        Args:
            package_name: Package to install
            
        Returns:
            True if installation successful
        """
        pkg_manager = self.get_package_manager()
        
        if pkg_manager == 'apt':
            cmd = f'sudo apt-get install -y {package_name}'
        elif pkg_manager in ['dnf', 'yum']:
            cmd = f'sudo {pkg_manager} install -y {package_name}'
        elif pkg_manager == 'pacman':
            cmd = f'sudo pacman -S --noconfirm {package_name}'
        else:
            return False
        
        result = self.connection.execute_command(cmd)
        return result['exit_code'] == 0
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information.
        
        Returns:
            System information dictionary
        """
        info = {
            'os': self.detect_os(),
            'package_manager': self.get_package_manager(),
        }
        
        # Get kernel version
        result = self.connection.execute_command('uname -r')
        if result['exit_code'] == 0:
            info['kernel'] = result['stdout'].strip()
        
        # Get uptime
        result = self.connection.execute_command('uptime -p')
        if result['exit_code'] == 0:
            info['uptime'] = result['stdout'].strip()
        
        return info
