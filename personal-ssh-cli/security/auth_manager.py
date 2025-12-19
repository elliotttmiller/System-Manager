"""
Authentication Manager

Handles SSH key management and authentication.
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess


class AuthManager:
    """Manages authentication and SSH keys."""
    
    def __init__(self, config_manager):
        """Initialize authentication manager.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config_manager = config_manager
        self.ssh_dir = Path.home() / ".ssh"
        self.ssh_dir.mkdir(mode=0o700, exist_ok=True)
    
    def list_keys(self) -> list:
        """List available SSH keys.
        
        Returns:
            List of key file paths
        """
        if not self.ssh_dir.exists():
            return []
        
        key_files = []
        for pattern in ["id_rsa", "id_ecdsa", "id_ed25519", "id_dsa"]:
            key_path = self.ssh_dir / pattern
            if key_path.exists():
                key_files.append(str(key_path))
        
        return key_files
    
    def generate_key(self, key_type: str = "ed25519", 
                    comment: Optional[str] = None,
                    passphrase: Optional[str] = None) -> Dict[str, Any]:
        """Generate new SSH key pair.
        
        Args:
            key_type: Key type (rsa, ecdsa, ed25519)
            comment: Optional comment for the key
            passphrase: Optional passphrase to protect the key
            
        Returns:
            Dictionary with key generation results
        """
        if key_type not in ["rsa", "ecdsa", "ed25519", "dsa"]:
            raise ValueError(f"Invalid key type: {key_type}")
        
        key_file = self.ssh_dir / f"id_{key_type}"
        
        if key_file.exists():
            return {
                'success': False,
                'error': f"Key file already exists: {key_file}",
            }
        
        try:
            cmd = [
                "ssh-keygen",
                "-t", key_type,
                "-f", str(key_file),
                "-N", passphrase or "",
            ]
            
            if comment:
                cmd.extend(["-C", comment])
            
            # Set key size for RSA
            if key_type == "rsa":
                cmd.extend(["-b", "4096"])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'private_key': str(key_file),
                    'public_key': str(key_file) + ".pub",
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }
    
    def get_public_key(self, key_file: str) -> Optional[str]:
        """Get public key content.
        
        Args:
            key_file: Path to private key file
            
        Returns:
            Public key content or None
        """
        pub_key_file = Path(key_file).with_suffix('.pub')
        
        if not pub_key_file.exists():
            # Try to generate public key from private key
            try:
                result = subprocess.run(
                    ["ssh-keygen", "-y", "-f", key_file],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except Exception:
                pass
            return None
        
        with open(pub_key_file, 'r') as f:
            return f.read().strip()
    
    def verify_key_passphrase(self, key_file: str, passphrase: str) -> bool:
        """Verify key passphrase.
        
        Args:
            key_file: Path to private key file
            passphrase: Passphrase to verify
            
        Returns:
            True if passphrase is correct
        """
        try:
            # Try to load the key with the passphrase
            import paramiko
            key_path = Path(key_file)
            
            if not key_path.exists():
                return False
            
            # Determine key type and load
            key_type = key_path.name.split('_')[1] if '_' in key_path.name else 'rsa'
            
            if 'rsa' in key_type:
                paramiko.RSAKey.from_private_key_file(str(key_path), password=passphrase)
            elif 'ecdsa' in key_type:
                paramiko.ECDSAKey.from_private_key_file(str(key_path), password=passphrase)
            elif 'ed25519' in key_type:
                paramiko.Ed25519Key.from_private_key_file(str(key_path), password=passphrase)
            else:
                return False
            
            return True
            
        except Exception:
            return False
    
    def add_key_to_agent(self, key_file: str) -> bool:
        """Add SSH key to ssh-agent.
        
        Args:
            key_file: Path to private key file
            
        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                ["ssh-add", key_file],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_key_fingerprint(self, key_file: str) -> Optional[str]:
        """Get SSH key fingerprint.
        
        Args:
            key_file: Path to key file
            
        Returns:
            Key fingerprint or None
        """
        try:
            result = subprocess.run(
                ["ssh-keygen", "-lf", key_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Extract fingerprint from output
                parts = result.stdout.strip().split()
                if len(parts) >= 2:
                    return parts[1]  # The fingerprint hash
            
            return None
            
        except Exception:
            return None
