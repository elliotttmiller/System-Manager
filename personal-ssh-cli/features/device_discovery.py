"""
Device Discovery

Local network device detection.
"""
import socket
import subprocess
from typing import List, Dict, Any, Optional


class DeviceDiscovery:
    """Discovers SSH-enabled devices on local network."""
    
    def __init__(self, config_manager):
        """Initialize device discovery.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config_manager = config_manager
    
    def scan_network(self, network_range: str = "192.168.1.0/24",
                    port: int = 22, timeout: float = 1.0) -> List[Dict[str, Any]]:
        """Scan network for SSH-enabled devices.
        
        Args:
            network_range: Network range to scan (CIDR notation)
            port: SSH port to check
            timeout: Connection timeout
            
        Returns:
            List of discovered devices
        """
        devices = []
        
        # Parse network range
        ips = self._expand_network_range(network_range)
        
        for ip in ips:
            if self._check_ssh_port(ip, port, timeout):
                device_info = {
                    'ip': ip,
                    'port': port,
                    'hostname': self._resolve_hostname(ip),
                }
                devices.append(device_info)
        
        return devices
    
    def _expand_network_range(self, network_range: str) -> List[str]:
        """Expand CIDR network range to list of IPs.
        
        Args:
            network_range: Network in CIDR notation
            
        Returns:
            List of IP addresses
        """
        try:
            import ipaddress
            network = ipaddress.ip_network(network_range, strict=False)
            return [str(ip) for ip in network.hosts()]
        except Exception:
            return []
    
    def _check_ssh_port(self, ip: str, port: int, timeout: float) -> bool:
        """Check if SSH port is open.
        
        Args:
            ip: IP address
            port: Port number
            timeout: Connection timeout
            
        Returns:
            True if port is open
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def _resolve_hostname(self, ip: str) -> Optional[str]:
        """Resolve IP to hostname.
        
        Args:
            ip: IP address
            
        Returns:
            Hostname or None
        """
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except Exception:
            return None
    
    def detect_local_devices(self) -> List[Dict[str, Any]]:
        """Detect SSH-enabled devices on local network.
        
        Returns:
            List of detected devices
        """
        # Get local network info
        local_ip = self._get_local_ip()
        if not local_ip:
            return []
        
        # Determine network range
        network_range = self._get_network_range(local_ip)
        
        # Scan network
        return self.scan_network(network_range)
    
    def _get_local_ip(self) -> Optional[str]:
        """Get local IP address.
        
        Returns:
            Local IP address or None
        """
        try:
            # Create a socket to determine local IP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            local_ip = sock.getsockname()[0]
            sock.close()
            return local_ip
        except Exception:
            return None
    
    def _get_network_range(self, local_ip: str) -> str:
        """Get network range from local IP.
        
        Args:
            local_ip: Local IP address
            
        Returns:
            Network range in CIDR notation
        """
        # Simple /24 network assumption
        parts = local_ip.split('.')
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
