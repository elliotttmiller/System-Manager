"""
Configuration Manager for Personal SSH CLI

Handles user configuration, device profiles, and persistent settings with encrypted storage.
"""
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64


class ConfigManager:
    """Manages application configuration and device profiles."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager.
        
        Args:
            config_dir: Custom configuration directory path
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Default to user's home directory
            self.config_dir = Path.home() / ".personal-ssh-cli"
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.yaml"
        self.profiles_file = self.config_dir / "profiles.yaml"
        self.secure_file = self.config_dir / ".secure.enc"
        self.key_file = self.config_dir / ".key"
        
        self._cipher = None
        self._config = None
        self._profiles = None
        
    def initialize(self, master_password: Optional[str] = None):
        """Initialize configuration with encryption key.
        
        Args:
            master_password: Master password for encryption (None for no encryption)
        """
        if master_password:
            self._setup_encryption(master_password)
        
        if not self.config_file.exists():
            self._create_default_config()
        
        if not self.profiles_file.exists():
            self._create_default_profiles()
    
    def _setup_encryption(self, master_password: str):
        """Setup encryption using master password."""
        salt = b'personal-ssh-cli-salt-v1'  # In production, use random salt stored securely
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        self._cipher = Fernet(key)
    
    def _create_default_config(self):
        """Create default configuration file."""
        default_config = {
            'version': '1.0.0',
            'settings': {
                'default_profile': None,
                'auto_reconnect': True,
                'connection_timeout': 30,
                'transfer_timeout': 300,
                'session_history_size': 1000,
                'color_output': True,
                'confirmation_prompts': True,
                'auto_save_sessions': True,
            },
            'security': {
                'verify_host_keys': True,
                'key_type': 'ed25519',
                'session_lock_timeout': 1800,  # 30 minutes
            },
            'performance': {
                'compression': True,
                'ssh_multiplexing': True,
                'bandwidth_limit': 0,  # 0 = unlimited
            },
            'ui': {
                'progress_bars': True,
                'notifications': True,
                'terminal_width': 'auto',
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
    
    def _create_default_profiles(self):
        """Create default profiles file."""
        default_profiles = {
            'profiles': {},
            'tags': {
                'work': [],
                'home': [],
                'servers': [],
            }
        }
        
        with open(self.profiles_file, 'w') as f:
            yaml.dump(default_profiles, f, default_flow_style=False)
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
        if self._config is None:
            with open(self.config_file, 'r') as f:
                self._config = yaml.safe_load(f)
        return self._config
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
        """
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        self._config = config
    
    def load_profiles(self) -> Dict[str, Any]:
        """Load device profiles from file.
        
        Returns:
            Profiles dictionary
        """
        if self._profiles is None:
            with open(self.profiles_file, 'r') as f:
                self._profiles = yaml.safe_load(f)
        return self._profiles
    
    def save_profiles(self, profiles: Dict[str, Any]):
        """Save device profiles to file.
        
        Args:
            profiles: Profiles dictionary to save
        """
        with open(self.profiles_file, 'w') as f:
            yaml.dump(profiles, f, default_flow_style=False)
        self._profiles = profiles
    
    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Get specific device profile.
        
        Args:
            name: Profile name
            
        Returns:
            Profile dictionary or None if not found
        """
        profiles = self.load_profiles()
        return profiles.get('profiles', {}).get(name)
    
    def add_profile(self, name: str, profile: Dict[str, Any]):
        """Add or update device profile.
        
        Args:
            name: Profile name
            profile: Profile configuration
        """
        profiles = self.load_profiles()
        if 'profiles' not in profiles:
            profiles['profiles'] = {}
        profiles['profiles'][name] = profile
        self.save_profiles(profiles)
    
    def delete_profile(self, name: str) -> bool:
        """Delete device profile.
        
        Args:
            name: Profile name
            
        Returns:
            True if deleted, False if not found
        """
        profiles = self.load_profiles()
        if name in profiles.get('profiles', {}):
            del profiles['profiles'][name]
            self.save_profiles(profiles)
            return True
        return False
    
    def list_profiles(self) -> list:
        """List all profile names.
        
        Returns:
            List of profile names
        """
        profiles = self.load_profiles()
        return list(profiles.get('profiles', {}).keys())
    
    def store_secure(self, key: str, value: str):
        """Store sensitive data securely.
        
        Args:
            key: Key name
            value: Value to store
        """
        if not self._cipher:
            raise RuntimeError("Encryption not initialized")
        
        # Load existing secure data
        secure_data = {}
        if self.secure_file.exists():
            with open(self.secure_file, 'rb') as f:
                encrypted = f.read()
                decrypted = self._cipher.decrypt(encrypted)
                secure_data = json.loads(decrypted.decode())
        
        # Update and save
        secure_data[key] = value
        encrypted = self._cipher.encrypt(json.dumps(secure_data).encode())
        with open(self.secure_file, 'wb') as f:
            f.write(encrypted)
    
    def retrieve_secure(self, key: str) -> Optional[str]:
        """Retrieve secure data.
        
        Args:
            key: Key name
            
        Returns:
            Value or None if not found
        """
        if not self._cipher:
            return None
        
        if not self.secure_file.exists():
            return None
        
        with open(self.secure_file, 'rb') as f:
            encrypted = f.read()
            decrypted = self._cipher.decrypt(encrypted)
            secure_data = json.loads(decrypted.decode())
        
        return secure_data.get(key)
    
    def get_setting(self, path: str, default: Any = None) -> Any:
        """Get configuration setting by dot-notation path.
        
        Args:
            path: Setting path (e.g., 'settings.auto_reconnect')
            default: Default value if not found
            
        Returns:
            Setting value
        """
        config = self.load_config()
        keys = path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set_setting(self, path: str, value: Any):
        """Set configuration setting by dot-notation path.
        
        Args:
            path: Setting path (e.g., 'settings.auto_reconnect')
            value: Value to set
        """
        config = self.load_config()
        keys = path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        self.save_config(config)
