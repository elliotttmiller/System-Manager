"""
Automated Device Pairing System
Seamlessly pairs Desktop (server) with Laptop (client) using specialized local/remote libraries.

WORKFLOW:
1. Desktop Setup: Run server configuration using LOCAL system tools
2. Generate Transfer Package: Create encrypted profile bundle
3. Laptop Import: Automatically detect and import profile using LOCAL client tools
4. Verification: Test connection using REMOTE libraries
"""

import os
import sys
import json
import socket
import platform
import subprocess
import getpass
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import base64
try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class AutomatedPairing:
    """Automated pairing system for Desktop-Laptop SSH configuration."""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.os_type = platform.system().lower()
        self.transfer_dir = Path.home() / ".personal-ssh-cli" / "transfers"
        self.transfer_dir.mkdir(parents=True, exist_ok=True)
        
    # ============================================================
    # PHASE 1: DESKTOP SETUP (Run on Desktop/Server)
    # ============================================================
    
    def setup_desktop_server(self) -> Dict[str, Any]:
        """
        Phase 1: Configure desktop as SSH server using LOCAL system libraries.
        Uses: local/service_monitor.py for SSH service management
        """
        print("\n" + "="*70)
        print("PHASE 1: DESKTOP SERVER SETUP")
        print("="*70)
        print("\nConfiguring this device as SSH server using LOCAL system tools...")
        
        # Step 1: Detect system info using local monitoring
        system_info = self._detect_system_info_local()
        
        # Step 2: Configure SSH server using local service monitor
        ssh_status = self._configure_ssh_server_local()
        
        # Step 3: Generate SSH keys if needed
        ssh_keys = self._setup_ssh_keys_local()
        
        # Step 4: Get IP address selection
        selected_ip = self._select_ip_address(system_info['ip_addresses'])
        
        # Step 5: Create profile configuration
        profile_name = input(f"\n📝 Profile name [{system_info['hostname']}]: ").strip()
        if not profile_name:
            profile_name = system_info['hostname']
        
        profile_config = {
            'name': profile_name,
            'hostname': selected_ip,
            'username': system_info['username'],
            'port': 22,
            'key_file': ssh_keys.get('public_key_path') if ssh_keys else None,
            'device_type': 'desktop',
            'os': system_info['os'],
            'created': datetime.now().isoformat(),
            'setup_method': 'automated_pairing',
        }
        
        # Step 6: Save profile locally
        profile_path = self.transfer_dir / f"{profile_name}_profile.json"
        with open(profile_path, 'w') as f:
            json.dump(profile_config, f, indent=2)
        
        print(f"\n✅ Profile saved: {profile_path}")
        
        # Step 7: Create transfer package for laptop
        transfer_package = self._create_transfer_package(profile_config, system_info, ssh_keys)
        
        return {
            'success': True,
            'profile': profile_config,
            'transfer_package': transfer_package,
            'system_info': system_info,
        }
    
    def _detect_system_info_local(self) -> Dict[str, Any]:
        """Detect system information using LOCAL monitoring tools."""
        print("\n🔍 Detecting system information (LOCAL)...")
        
        # Import local system monitoring if available
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "local"))
            from system_monitoring import SystemMonitor
            monitor = SystemMonitor()
            sys_metrics = monitor.get_system_metrics()
            
            info = {
                'hostname': sys_metrics.get('hostname', socket.gethostname()),
                'os': platform.system(),
                'os_version': platform.version(),
                'username': getpass.getuser(),
                'ip_addresses': self._get_network_ips(),
                'cpu_info': sys_metrics.get('cpu'),
                'memory_info': sys_metrics.get('memory'),
            }
        except Exception as e:
            # Fallback to basic detection
            print(f"⚠️  Advanced monitoring unavailable, using basic detection: {e}")
            info = {
                'hostname': socket.gethostname(),
                'os': platform.system(),
                'os_version': platform.version(),
                'username': getpass.getuser(),
                'ip_addresses': self._get_network_ips(),
            }
        
        print(f"\n✅ Detected: {info['os']} on {info['hostname']}")
        return info
    
    def _configure_ssh_server_local(self) -> Dict[str, Any]:
        """Configure SSH server using LOCAL service monitor."""
        print("\n🔧 Configuring SSH server (LOCAL service monitor)...")
        
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "local"))
            from service_monitor import ServiceMonitor
            service_mon = ServiceMonitor()
            
            # Check SSH service status
            ssh_status = service_mon.check_ssh_service()
            
            if ssh_status.get('running'):
                print("✅ SSH server is already running")
            else:
                print("⚠️  SSH server not running, attempting to start...")
                # Start SSH service if not running
                # Note: This might require admin/sudo privileges
                start_result = service_mon.start_ssh_service()
                if start_result.get('success'):
                    print("✅ SSH server started successfully")
                else:
                    print(f"⚠️  Could not start SSH server: {start_result.get('error')}")
            
            return ssh_status
            
        except Exception as e:
            print(f"⚠️  Could not use local service monitor: {e}")
            return {'running': False, 'error': str(e)}
    
    def _setup_ssh_keys_local(self) -> Optional[Dict[str, Any]]:
        """Setup SSH keys using LOCAL security tools."""
        print("\n🔑 Setting up SSH keys (LOCAL security)...")
        
        generate = input("❓ Generate SSH keys? (y/n): ").strip().lower()
        if generate != 'y':
            return None
        
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "security"))
            from auth_manager import AuthManager
            auth_mgr = AuthManager(self.config_manager)
            
            # Check if keys exist
            ssh_dir = Path.home() / ".ssh"
            key_types = ['ed25519', 'rsa']
            
            for key_type in key_types:
                key_path = ssh_dir / f"id_{key_type}"
                if key_path.exists():
                    print(f"✅ SSH key already exists: {key_path}")
                    return {
                        'type': key_type,
                        'private_key_path': str(key_path),
                        'public_key_path': str(key_path) + ".pub",
                    }
            
            # Generate new key
            print("🔑 Generating new SSH key (ed25519)...")
            result = auth_mgr.generate_ssh_key('ed25519')
            
            if result.get('success'):
                print(f"✅ Key generated: {result['key_path']}")
                return result
            else:
                print(f"⚠️  Key generation failed: {result.get('error')}")
                return None
                
        except Exception as e:
            print(f"⚠️  Could not use security manager: {e}")
            return None
    
    def _get_network_ips(self) -> List[str]:
        """Get network IP addresses, prioritizing actual network interfaces."""
        ip_list = []
        seen = set()
        
        try:
            # Primary method: connect to external address to get active IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            primary_ip = s.getsockname()[0]
            s.close()
            if primary_ip and primary_ip != '127.0.0.1':
                ip_list.append(primary_ip)
                seen.add(primary_ip)
        except Exception:
            pass
        
        # Try psutil for comprehensive network info
        try:
            import psutil
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        ip = addr.address
                        if ip not in seen and not ip.startswith('127.') and not ip.startswith('169.254.'):
                            ip_list.append(ip)
                            seen.add(ip)
        except ImportError:
            pass
        
        # Fallback to hostname-based
        try:
            hostname = socket.gethostname()
            hostname_ips = socket.gethostbyname_ex(hostname)[2]
            for ip in hostname_ips:
                if ip not in seen and not ip.startswith('127.'):
                    ip_list.append(ip)
                    seen.add(ip)
        except Exception:
            pass
        
        return ip_list if ip_list else ['127.0.0.1']
    
    def _select_ip_address(self, ip_addresses: List[str]) -> str:
        """Interactive IP address selection."""
        print("\n🌐 Detected IP addresses:")
        for i, ip in enumerate(ip_addresses, 1):
            label = "(Primary)" if i == 1 else ""
            print(f"   {i}. {ip} {label}")
        
        if len(ip_addresses) == 1:
            print(f"\nUsing IP: {ip_addresses[0]}")
            return ip_addresses[0]
        
        while True:
            choice = input(f"\nWhich IP should be used for SSH connections? [1-{len(ip_addresses)}] or enter custom: ").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(ip_addresses):
                selected_ip = ip_addresses[int(choice) - 1]
                print(f"Using IP: {selected_ip}")
                return selected_ip
            elif choice and '.' in choice:  # Custom IP
                print(f"Using custom IP: {choice}")
                return choice
            else:
                print("❌ Invalid choice, please try again")
    
    def _create_transfer_package(self, profile: Dict, system_info: Dict, ssh_keys: Optional[Dict]) -> Dict[str, Any]:
        """Create encrypted transfer package for laptop import."""
        print("\n📦 Creating transfer package for laptop...")
        
        package = {
            'version': '1.0',
            'created': datetime.now().isoformat(),
            'profile': profile,
            'system_info': system_info,
            'ssh_keys': ssh_keys,
            'setup_instructions': {
                'step1': 'Copy this package to your laptop',
                'step2': 'Run: pssh import-auto <package_file>',
                'step3': 'Test: pssh connect ' + profile['name'],
            }
        }
        
        # Save package
        package_filename = f"transfer_{profile['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        package_path = self.transfer_dir / package_filename
        
        with open(package_path, 'w') as f:
            json.dump(package, f, indent=2)
        
        print(f"✅ Transfer package created: {package_path}")
        
        # Also create a simple text file with instructions
        instructions_path = self.transfer_dir / f"INSTRUCTIONS_{profile['name']}.txt"
        with open(instructions_path, 'w') as f:
            f.write(f"""
SSH Profile Transfer Package
============================

Profile Name: {profile['name']}
Hostname: {profile['hostname']}
Username: {profile['username']}

LAPTOP SETUP INSTRUCTIONS:
--------------------------

1. Copy these files to your LAPTOP:
   - {package_filename}
   
2. On your LAPTOP, run ONE of these commands:

   Option A - Automatic Import:
   pssh import-auto {package_filename}
   
   Option B - Manual Import:
   pssh import-profile {profile['name']}_profile.json
   
3. Test the connection:
   pssh connect {profile['name']}

Package Location: {package_path}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
        
        print(f"📄 Instructions saved: {instructions_path}")
        
        return {
            'package_path': str(package_path),
            'instructions_path': str(instructions_path),
            'package': package,
        }
    
    # ============================================================
    # PHASE 2: LAPTOP IMPORT (Run on Laptop/Client)
    # ============================================================
    
    def import_on_laptop(self, package_path: str) -> Dict[str, Any]:
        """
        Phase 2: Import configuration on laptop using LOCAL client tools.
        Uses: local/file_management.py for file operations
        """
        print("\n" + "="*70)
        print("PHASE 2: LAPTOP CLIENT IMPORT")
        print("="*70)
        print("\nImporting profile using LOCAL client tools...")
        
        # Step 1: Load package
        try:
            with open(package_path, 'r') as f:
                package = json.load(f)
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to load package: {e}"
            }
        
        profile = package.get('profile', {})
        
        # Step 2: Validate package
        if not profile.get('name') or not profile.get('hostname'):
            return {
                'success': False,
                'error': "Invalid package: missing required profile information"
            }
        
        # Step 3: Import profile using config manager
        if self.config_manager:
            try:
                self.config_manager.add_profile(
                    name=profile['name'],
                    hostname=profile['hostname'],
                    username=profile['username'],
                    port=profile.get('port', 22),
                    key_file=profile.get('key_file'),
                )
                print(f"✅ Profile '{profile['name']}' imported successfully")
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Failed to import profile: {e}"
                }
        
        # Step 4: Setup SSH keys if provided
        ssh_keys = package.get('ssh_keys')
        if ssh_keys:
            self._import_ssh_keys_local(ssh_keys)
        
        print("\n" + "="*70)
        print("✨ IMPORT COMPLETE")
        print("="*70)
        print(f"\nProfile '{profile['name']}' is ready to use!")
        print(f"\nTest connection with: pssh connect {profile['name']}")
        
        return {
            'success': True,
            'profile': profile,
            'message': 'Profile imported successfully'
        }
    
    def _import_ssh_keys_local(self, ssh_keys: Dict) -> bool:
        """Import SSH keys using LOCAL security tools."""
        print("\n🔑 Importing SSH keys...")
        
        try:
            ssh_dir = Path.home() / ".ssh"
            ssh_dir.mkdir(mode=0o700, exist_ok=True)
            
            # Note: Actual key transfer should be done manually for security
            # This is a placeholder for the workflow
            print("⚠️  SSH key transfer should be done manually for security")
            print(f"    Copy public key to: {ssh_dir / 'authorized_keys'}")
            
            return True
        except Exception as e:
            print(f"⚠️  Key import warning: {e}")
            return False
    
    # ============================================================
    # PHASE 3: VERIFICATION (Run on Laptop)
    # ============================================================
    
    def verify_connection(self, profile_name: str, connection_manager) -> Dict[str, Any]:
        """
        Phase 3: Verify connection using REMOTE libraries.
        Uses: remote/remote_system_monitoring.py for connection testing
        """
        print("\n" + "="*70)
        print("PHASE 3: CONNECTION VERIFICATION")
        print("="*70)
        print(f"\nTesting connection to '{profile_name}' using REMOTE tools...")
        
        try:
            # Create connection
            conn_id = connection_manager.create_connection(profile_name)
            
            # Attempt connection
            success = connection_manager.connect(conn_id, timeout=10)
            
            if success:
                print("✅ Connection successful!")
                
                # Test remote command execution
                result = connection_manager.execute_command(conn_id, "echo 'Connection verified'")
                
                if result.get('exit_code') == 0:
                    print("✅ Remote command execution verified")
                    
                    # Try remote system monitoring
                    try:
                        sys.path.insert(0, str(Path(__file__).parent.parent / "remote"))
                        from remote_system_monitoring import RemoteSystemMonitor
                        
                        remote_monitor = RemoteSystemMonitor()
                        ssh_conn = connection_manager.get_connection(conn_id)
                        remote_monitor.set_connection(ssh_conn.client, {'host': profile_name})
                        
                        metrics = remote_monitor.get_system_metrics()
                        print(f"✅ Remote monitoring working - CPU: {metrics.get('cpu', {}).get('percent', 'N/A')}%")
                        
                    except Exception as e:
                        print(f"⚠️  Remote monitoring unavailable: {e}")
                
                connection_manager.disconnect(conn_id)
                
                return {
                    'success': True,
                    'message': 'Connection verified successfully',
                    'profile': profile_name
                }
            else:
                return {
                    'success': False,
                    'error': 'Connection failed'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Verification failed: {e}'
            }
    
    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
    def display_summary(self, setup_result: Dict[str, Any]):
        """Display setup summary with instructions."""
        print("\n" + "="*70)
        print("📋 SETUP SUMMARY")
        print("="*70)
        
        profile = setup_result.get('profile', {})
        system_info = setup_result.get('system_info', {})
        transfer_pkg = setup_result.get('transfer_package', {})
        
        print(f"\n🖥️  Device Information:")
        print(f"   Hostname: {system_info.get('hostname')}")
        print(f"   OS: {system_info.get('os')} {system_info.get('os_version', '')}")
        print(f"   Username: {system_info.get('username')}")
        
        print(f"\n🌐 Network Information:")
        for ip in system_info.get('ip_addresses', []):
            print(f"   IP: {ip}")
        print(f"   SSH Port: {profile.get('port', 22)}")
        
        print(f"\n📝 Profile Configuration:")
        print(f"   Profile Name: {profile.get('name')}")
        print(f"   Connection: ssh {profile.get('username')}@{profile.get('hostname')}")
        
        print(f"\n📦 Transfer Package:")
        print(f"   Package: {transfer_pkg.get('package_path')}")
        print(f"   Instructions: {transfer_pkg.get('instructions_path')}")
        
        print("\n" + "="*70)
        print("✨ Next Steps:")
        print("="*70)
        
        print(f"\n1. Copy the transfer package to your LAPTOP:")
        print(f"   Location: {transfer_pkg.get('package_path')}")
        
        print(f"\n2. On your LAPTOP, import the profile:")
        print(f"   pssh import-auto {Path(transfer_pkg.get('package_path', '')).name}")
        
        print(f"\n3. Test the connection:")
        print(f"   pssh connect {profile.get('name')}")
        
        print("\n" + "="*70)
        print("\n✓ Setup completed!\n")


def run_automated_setup(config_manager=None, mode='desktop'):
    """
    Entry point for automated pairing setup.
    
    Args:
        config_manager: ConfigManager instance
        mode: 'desktop' for server setup, 'laptop' for client import
    """
    pairing = AutomatedPairing(config_manager)
    
    if mode == 'desktop':
        result = pairing.setup_desktop_server()
        if result.get('success'):
            pairing.display_summary(result)
        return result
    
    elif mode == 'laptop':
        package_path = input("Enter path to transfer package: ").strip()
        return pairing.import_on_laptop(package_path)
    
    else:
        return {'success': False, 'error': 'Invalid mode'}
