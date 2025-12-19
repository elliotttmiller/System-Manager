# -*- coding: utf-8 -*-
"""
Automated Setup for SSH Server Configuration

This script runs on the REMOTE device (desktop/server) to automatically:
1. Detect system information (OS, IP, hostname)
2. Configure SSH server
3. Generate configuration profile
4. Optionally set up SSH keys
"""
import os
import sys
import platform
import socket
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import getpass

# Ensure UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


class AutoSetup:
    """Automated setup for SSH server and configuration."""
    
    def __init__(self):
        self.system_info = {}
        self.config = {}
        self.os_type = platform.system().lower()
        
    def detect_system_info(self) -> Dict[str, Any]:
        """Detect system information automatically."""
        print("🔍 Detecting system information...")
        
        info = {
            'hostname': socket.gethostname(),
            'os': platform.system(),
            'os_version': platform.version(),
            'architecture': platform.machine(),
            'python_version': platform.python_version(),
            'username': getpass.getuser(),
            'ip_addresses': self._get_ip_addresses(),
            'ssh_port': 22,  # Default
        }
        
        self.system_info = info
        return info
    
    def _get_ip_addresses(self) -> List[str]:
        """Get all IP addresses of the system, prioritizing actual network IPs."""
        ip_list = []
        seen = set()
        
        try:
            # Method 1: Get primary network IP by connecting to external address
            # This is most reliable for getting the actual network interface IP
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('8.8.8.8', 80))  # Google DNS - doesn't need to be reachable
                primary_ip = s.getsockname()[0]
                s.close()
                if primary_ip and primary_ip != '127.0.0.1':
                    ip_list.append(primary_ip)
                    seen.add(primary_ip)
            except Exception:
                pass
            
            # Method 2: Use psutil if available for all network interfaces
            try:
                import psutil
                for interface, addrs in psutil.net_if_addrs().items():
                    for addr in addrs:
                        if addr.family == socket.AF_INET:  # IPv4
                            ip = addr.address
                            if ip not in seen and not ip.startswith('127.') and not ip.startswith('169.254.'):
                                ip_list.append(ip)
                                seen.add(ip)
            except ImportError:
                pass
            
            # Method 3: Get hostname-based addresses
            try:
                hostname = socket.gethostname()
                hostname_ips = socket.gethostbyname_ex(hostname)[2]
                for ip in hostname_ips:
                    if ip not in seen and not ip.startswith('127.'):
                        ip_list.append(ip)
                        seen.add(ip)
            except Exception:
                pass
            
            # Add localhost if no other IPs found
            if not ip_list:
                ip_list = ['127.0.0.1']
                
        except Exception as e:
            print(f"Warning: Could not detect all IPs: {e}")
            ip_list = ['127.0.0.1']
        
        return ip_list
    
    def check_ssh_server_status(self) -> Dict[str, Any]:
        """Check if SSH server is installed and running."""
        print("\n🔍 Checking SSH server status...")
        
        status = {
            'installed': False,
            'running': False,
            'service_name': '',
            'port': 22
        }
        
        if self.os_type == 'windows':
            status.update(self._check_windows_ssh())
        elif self.os_type == 'linux':
            status.update(self._check_linux_ssh())
        elif self.os_type == 'darwin':  # macOS
            status.update(self._check_macos_ssh())
        
        return status
    
    def _check_windows_ssh(self) -> Dict[str, Any]:
        """Check SSH server status on Windows."""
        try:
            # Check if OpenSSH Server is installed
            result = subprocess.run(
                ['powershell', '-Command', 
                 'Get-WindowsCapability -Online | Where-Object Name -like "OpenSSH.Server*"'],
                capture_output=True, text=True, timeout=10
            )
            
            installed = 'Installed' in result.stdout
            
            # Check if service is running
            result = subprocess.run(
                ['powershell', '-Command', 
                 'Get-Service -Name sshd -ErrorAction SilentlyContinue | Select-Object Status'],
                capture_output=True, text=True, timeout=10
            )
            
            running = 'Running' in result.stdout
            
            return {
                'installed': installed,
                'running': running,
                'service_name': 'sshd'
            }
        except Exception as e:
            print(f"⚠️  Warning: Could not check Windows SSH status: {e}")
            return {'installed': False, 'running': False, 'service_name': 'sshd'}
    
    def _check_linux_ssh(self) -> Dict[str, Any]:
        """Check SSH server status on Linux."""
        try:
            # Check if SSH server is installed
            installed = any([
                Path('/usr/sbin/sshd').exists(),
                Path('/usr/bin/sshd').exists(),
                subprocess.run(['which', 'sshd'], 
                             capture_output=True).returncode == 0
            ])
            
            # Check if service is running
            running = False
            service_name = 'ssh'
            
            for service in ['sshd', 'ssh']:
                result = subprocess.run(
                    ['systemctl', 'is-active', service],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    running = True
                    service_name = service
                    break
            
            return {
                'installed': installed,
                'running': running,
                'service_name': service_name
            }
        except Exception as e:
            print(f"⚠️  Warning: Could not check Linux SSH status: {e}")
            return {'installed': False, 'running': False, 'service_name': 'ssh'}
    
    def _check_macos_ssh(self) -> Dict[str, Any]:
        """Check SSH server status on macOS."""
        try:
            # Check if SSH is enabled
            result = subprocess.run(
                ['systemsetup', '-getremotelogin'],
                capture_output=True, text=True
            )
            
            running = 'On' in result.stdout
            
            return {
                'installed': True,  # macOS always has SSH
                'running': running,
                'service_name': 'ssh'
            }
        except Exception as e:
            print(f"⚠️  Warning: Could not check macOS SSH status: {e}")
            return {'installed': True, 'running': False, 'service_name': 'ssh'}
    
    def enable_ssh_server(self) -> bool:
        """Enable and start SSH server."""
        print("\n🔧 Enabling SSH server...")
        
        if self.os_type == 'windows':
            return self._enable_windows_ssh()
        elif self.os_type == 'linux':
            return self._enable_linux_ssh()
        elif self.os_type == 'darwin':
            return self._enable_macos_ssh()
        
        return False
    
    def _enable_windows_ssh(self) -> bool:
        """Enable SSH server on Windows."""
        try:
            print("Installing OpenSSH Server...")
            subprocess.run(
                ['powershell', '-Command',
                 'Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0'],
                check=True
            )
            
            print("Starting SSH service...")
            subprocess.run(
                ['powershell', '-Command', 'Start-Service sshd'],
                check=True
            )
            
            print("Setting SSH service to start automatically...")
            subprocess.run(
                ['powershell', '-Command',
                 'Set-Service -Name sshd -StartupType Automatic'],
                check=True
            )
            
            # Configure firewall
            print("Configuring firewall...")
            subprocess.run(
                ['powershell', '-Command',
                 'New-NetFirewallRule -Name sshd -DisplayName "OpenSSH Server (sshd)" '
                 '-Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 '
                 '-ErrorAction SilentlyContinue'],
                check=False  # Don't fail if rule already exists
            )
            
            print("✅ SSH server enabled successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error enabling SSH server: {e}")
            print("💡 Try running as Administrator")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def _enable_linux_ssh(self) -> bool:
        """Enable SSH server on Linux."""
        try:
            # Try to install if not installed
            print("Installing SSH server...")
            
            # Detect package manager
            if Path('/usr/bin/apt').exists():
                subprocess.run(['sudo', 'apt', 'update'], check=False)
                subprocess.run(['sudo', 'apt', 'install', '-y', 'openssh-server'], check=True)
            elif Path('/usr/bin/yum').exists():
                subprocess.run(['sudo', 'yum', 'install', '-y', 'openssh-server'], check=True)
            elif Path('/usr/bin/dnf').exists():
                subprocess.run(['sudo', 'dnf', 'install', '-y', 'openssh-server'], check=True)
            
            # Start and enable service
            print("Starting SSH service...")
            subprocess.run(['sudo', 'systemctl', 'start', 'ssh'], check=False)
            subprocess.run(['sudo', 'systemctl', 'start', 'sshd'], check=False)
            subprocess.run(['sudo', 'systemctl', 'enable', 'ssh'], check=False)
            subprocess.run(['sudo', 'systemctl', 'enable', 'sshd'], check=False)
            
            print("✅ SSH server enabled successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Try running with sudo privileges")
            return False
    
    def _enable_macos_ssh(self) -> bool:
        """Enable SSH server on macOS."""
        try:
            print("Enabling Remote Login...")
            subprocess.run(
                ['sudo', 'systemsetup', '-setremotelogin', 'on'],
                check=True
            )
            
            print("✅ SSH server enabled successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Try running with sudo privileges")
            return False
    
    def generate_ssh_keys(self, key_type: str = 'ed25519') -> Optional[Path]:
        """Generate SSH key pair if not exists."""
        print(f"\n🔑 Checking SSH keys ({key_type})...")
        
        ssh_dir = Path.home() / '.ssh'
        ssh_dir.mkdir(mode=0o700, exist_ok=True)
        
        key_file = ssh_dir / f'id_{key_type}'
        
        if key_file.exists():
            print(f"✅ SSH key already exists: {key_file}")
            return key_file
        
        try:
            print(f"Generating new {key_type} key pair...")
            subprocess.run(
                ['ssh-keygen', '-t', key_type, '-f', str(key_file), '-N', ''],
                check=True
            )
            print(f"✅ SSH key generated: {key_file}")
            return key_file
            
        except Exception as e:
            print(f"⚠️  Warning: Could not generate SSH key: {e}")
            return None
    
    def generate_profile_config(self, profile_name: Optional[str] = None) -> Dict[str, Any]:
        """Generate profile configuration for the client."""
        if not profile_name:
            profile_name = self.system_info.get('hostname', 'remote-device')
        
        # Choose best IP address
        ip_addresses = self.system_info.get('ip_addresses', [])
        primary_ip = ip_addresses[0] if ip_addresses else 'UNKNOWN'
        
        config = {
            'profile_name': profile_name,
            'host': primary_ip,
            'hostname': self.system_info.get('hostname'),
            'username': self.system_info.get('username'),
            'port': self.system_info.get('ssh_port', 22),
            'auth_method': 'key',  # Prefer key-based auth
            'key_file': f"~/.ssh/id_ed25519",
            'description': f"{self.system_info.get('os')} - {self.system_info.get('hostname')}",
            'os_type': self.system_info.get('os'),
            'alternative_ips': ip_addresses,
        }
        
        self.config = config
        return config
    
    def save_config_file(self, output_dir: Optional[Path] = None) -> Path:
        """Save configuration to a file that can be imported."""
        if not output_dir:
            output_dir = Path.home() / '.personal-ssh-cli'
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = output_dir / f"{self.config.get('profile_name', 'device')}_profile.json"
        
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print(f"\n✅ Configuration saved to: {config_file}")
        return config_file
    
    def display_summary(self):
        """Display setup summary."""
        print("\n" + "="*70)
        print("📋 SETUP SUMMARY")
        print("="*70)
        print(f"\n🖥️  Device Information:")
        print(f"   Hostname: {self.system_info.get('hostname')}")
        print(f"   OS: {self.system_info.get('os')} {self.system_info.get('os_version')}")
        print(f"   Username: {self.system_info.get('username')}")
        print(f"\n🌐 Network Information:")
        for idx, ip in enumerate(self.system_info.get('ip_addresses', []), 1):
            print(f"   IP {idx}: {ip}")
        print(f"   SSH Port: {self.system_info.get('ssh_port')}")
        
        print(f"\n📝 Profile Configuration:")
        print(f"   Profile Name: {self.config.get('profile_name')}")
        print(f"   Connection: ssh {self.config.get('username')}@{self.config.get('host')}")
        
        print("\n" + "="*70)
        print("✨ Next Steps:")
        print("="*70)
        print("\n1. Copy the configuration file to your CLIENT device (laptop)")
        profile_name = self.config.get('profile_name')
        config_path = Path.home() / '.personal-ssh-cli' / f'{profile_name}_profile.json'
        print(f"   Location: {config_path}")
        
        print("\n2. On your CLIENT device, import the profile:")
        print(f"   pssh import-profile {profile_name}_profile.json")
        
        print("\n3. Test the connection:")
        print(f"   pssh connect {profile_name}")
        
        print("\n💡 Alternative - Manual Setup on Client:")
        print(f"   pssh add-profile {self.config.get('profile_name')}")
        print(f"   Host: {self.config.get('host')}")
        print(f"   Username: {self.config.get('username')}")
        print(f"   Port: {self.config.get('port')}")
        print("\n" + "="*70)
    
    def run_interactive_setup(self):
        """Run the complete interactive setup process."""
        print("="*70)
        print("AUTOMATED SSH SERVER SETUP")
        print("="*70)
        print("\nThis script will configure this device as an SSH server")
        print("that can be accessed from your other devices.\n")
        
        # Step 1: Detect system
        self.detect_system_info()
        print(f"\nDetected: {self.system_info['os']} on {self.system_info['hostname']}")
        
        # Display all detected IP addresses
        ip_addresses = self.system_info.get('ip_addresses', [])
        if len(ip_addresses) > 1:
            print("\nDetected IP addresses:")
            for idx, ip in enumerate(ip_addresses, 1):
                marker = " (Primary)" if idx == 1 else ""
                print(f"   {idx}. {ip}{marker}")
            
            # Let user choose or verify
            choice = input(f"\nWhich IP should be used for SSH connections? [1-{len(ip_addresses)}] or enter custom: ").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(ip_addresses):
                selected_ip = ip_addresses[int(choice) - 1]
                # Move selected IP to front
                ip_addresses.remove(selected_ip)
                ip_addresses.insert(0, selected_ip)
                self.system_info['ip_addresses'] = ip_addresses
                print(f"Using IP: {selected_ip}")
            elif choice and '.' in choice:  # Custom IP entered
                custom_ip = choice
                if custom_ip not in ip_addresses:
                    ip_addresses.insert(0, custom_ip)
                else:
                    ip_addresses.remove(custom_ip)
                    ip_addresses.insert(0, custom_ip)
                self.system_info['ip_addresses'] = ip_addresses
                print(f"Using IP: {custom_ip}")
            else:
                print(f"Using default IP: {ip_addresses[0]}")
        else:
            print(f"Detected IP: {ip_addresses[0] if ip_addresses else 'Unknown'}")
        
        # Step 2: Check SSH status
        ssh_status = self.check_ssh_server_status()
        
        if not ssh_status['running']:
            print("\n❌ SSH server is not running")
            response = input("\n❓ Enable SSH server? (y/n): ").lower()
            
            if response == 'y':
                success = self.enable_ssh_server()
                if not success:
                    print("\n❌ Failed to enable SSH server. Please enable manually.")
                    return False
            else:
                print("\n⚠️  SSH server must be enabled to continue.")
                return False
        else:
            print("\n✅ SSH server is already running")
        
        # Step 3: SSH Keys
        response = input("\n❓ Generate SSH keys? (y/n): ").lower()
        if response == 'y':
            self.generate_ssh_keys()
        
        # Step 4: Generate profile
        profile_name = input(f"\n❓ Profile name [{self.system_info['hostname']}]: ").strip()
        if not profile_name:
            profile_name = self.system_info['hostname']
        
        self.generate_profile_config(profile_name)
        
        # Step 5: Save configuration
        config_file = self.save_config_file()
        
        # Step 6: Display summary
        self.display_summary()
        
        return True


def main():
    """Main entry point."""
    setup = AutoSetup()
    
    try:
        setup.run_interactive_setup()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
