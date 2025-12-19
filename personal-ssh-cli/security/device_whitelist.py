"""
Device Whitelist Manager

Manages approved devices and host key verification.
"""
import json
import hashlib
from pathlib import Path
from typing import Dict, Optional, Any, List
from datetime import datetime


class DeviceWhitelist:
    """Manages whitelist of approved devices."""
    
    def __init__(self, config_manager):
        """Initialize device whitelist.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config_manager = config_manager
        self.whitelist_file = config_manager.config_dir / "whitelist.json"
        self.whitelist = self._load_whitelist()
    
    def _load_whitelist(self) -> Dict[str, Any]:
        """Load whitelist from file.
        
        Returns:
            Whitelist dictionary
        """
        if not self.whitelist_file.exists():
            return {'devices': {}}
        
        try:
            with open(self.whitelist_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {'devices': {}}
    
    def _save_whitelist(self):
        """Save whitelist to file."""
        with open(self.whitelist_file, 'w') as f:
            json.dump(self.whitelist, f, indent=2)
    
    def add_device(self, hostname: str, host_key: str, 
                   fingerprint: str, metadata: Optional[Dict] = None) -> bool:
        """Add device to whitelist.
        
        Args:
            hostname: Device hostname or IP
            host_key: SSH host key
            fingerprint: Key fingerprint
            metadata: Optional device metadata
            
        Returns:
            True if added successfully
        """
        device_id = self._generate_device_id(hostname)
        
        device_info = {
            'hostname': hostname,
            'host_key': host_key,
            'fingerprint': fingerprint,
            'added_at': datetime.now().isoformat(),
            'last_verified': datetime.now().isoformat(),
            'metadata': metadata or {},
        }
        
        self.whitelist['devices'][device_id] = device_info
        self._save_whitelist()
        
        return True
    
    def remove_device(self, hostname: str) -> bool:
        """Remove device from whitelist.
        
        Args:
            hostname: Device hostname or IP
            
        Returns:
            True if removed, False if not found
        """
        device_id = self._generate_device_id(hostname)
        
        if device_id in self.whitelist['devices']:
            del self.whitelist['devices'][device_id]
            self._save_whitelist()
            return True
        
        return False
    
    def is_whitelisted(self, hostname: str) -> bool:
        """Check if device is whitelisted.
        
        Args:
            hostname: Device hostname or IP
            
        Returns:
            True if device is whitelisted
        """
        device_id = self._generate_device_id(hostname)
        return device_id in self.whitelist['devices']
    
    def get_device(self, hostname: str) -> Optional[Dict[str, Any]]:
        """Get device information.
        
        Args:
            hostname: Device hostname or IP
            
        Returns:
            Device information or None
        """
        device_id = self._generate_device_id(hostname)
        return self.whitelist['devices'].get(device_id)
    
    def verify_host_key(self, hostname: str, host_key: str, 
                       fingerprint: str) -> bool:
        """Verify host key matches whitelist.
        
        Args:
            hostname: Device hostname or IP
            host_key: Current SSH host key
            fingerprint: Current key fingerprint
            
        Returns:
            True if host key matches
        """
        device = self.get_device(hostname)
        
        if not device:
            return False
        
        # Check if host key matches
        if device['host_key'] != host_key or device['fingerprint'] != fingerprint:
            return False
        
        # Update last verified timestamp
        device_id = self._generate_device_id(hostname)
        self.whitelist['devices'][device_id]['last_verified'] = datetime.now().isoformat()
        self._save_whitelist()
        
        return True
    
    def list_devices(self) -> List[Dict[str, Any]]:
        """List all whitelisted devices.
        
        Returns:
            List of device information
        """
        return [
            {
                'device_id': device_id,
                **device_info
            }
            for device_id, device_info in self.whitelist['devices'].items()
        ]
    
    def update_device_metadata(self, hostname: str, metadata: Dict[str, Any]):
        """Update device metadata.
        
        Args:
            hostname: Device hostname or IP
            metadata: Metadata to update
        """
        device_id = self._generate_device_id(hostname)
        
        if device_id in self.whitelist['devices']:
            self.whitelist['devices'][device_id]['metadata'].update(metadata)
            self._save_whitelist()
    
    def _generate_device_id(self, hostname: str) -> str:
        """Generate unique device ID from hostname.
        
        Args:
            hostname: Device hostname or IP
            
        Returns:
            Device ID
        """
        return hashlib.sha256(hostname.encode()).hexdigest()[:16]
