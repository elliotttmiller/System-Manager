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
                    port: int = 22, timeout: float = 0.5, max_workers: int = 50) -> List[Dict[str, Any]]:
        """Scan network for SSH-enabled devices.

        This used to scan sequentially which could take many minutes on /24 ranges.
        Use a ThreadPoolExecutor to parallelize TCP port checks so the scan completes
        much faster. The default timeout was reduced to 0.5s and max_workers defaults
        to 50 to balance speed and network load.

        Args:
            network_range: Network range to scan (CIDR notation)
            port: SSH port to check
            timeout: Connection timeout per host (seconds)
            max_workers: Number of concurrent worker threads

        Returns:
            List of discovered devices
        """
        devices: List[Dict[str, Any]] = []

        # Parse network range
        ips = self._expand_network_range(network_range)
        if not ips:
            return devices

        # Limit workers to a sensible number
        try:
            from concurrent.futures import ThreadPoolExecutor, as_completed
        except Exception:
            # Fallback to sequential scan if concurrent module unavailable
            for ip in ips:
                if self._check_ssh_port(ip, port, timeout):
                    devices.append({'ip': ip, 'port': port, 'hostname': self._resolve_hostname(ip)})
            return devices

        workers = min(max_workers, len(ips))

        futures = {}
        with ThreadPoolExecutor(max_workers=workers) as exc:
            for ip in ips:
                fut = exc.submit(self._check_ssh_port, ip, port, timeout)
                futures[fut] = ip

            for fut in as_completed(futures):
                ip = futures[fut]
                try:
                    is_open = fut.result()
                except Exception:
                    is_open = False

                if is_open:
                    devices.append({
                        'ip': ip,
                        'port': port,
                        'hostname': self._resolve_hostname(ip),
                    })

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
