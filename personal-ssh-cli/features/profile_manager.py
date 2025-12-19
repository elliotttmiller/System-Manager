"""
Profile Manager
Comprehensive profile management with intelligent routing to LOCAL/REMOTE libraries.

ARCHITECTURE:
- Profile CRUD operations (Create, Read, Update, Delete)
- Automatic feature routing based on profile context
- LOCAL library integration for client-side operations
- REMOTE library integration for server-side operations
- Profile validation and health checks
"""

# Standard Library Imports
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Third-Party Imports
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

# Local package imports (use package-qualified names so language servers can resolve)
try:
    from local.system_monitoring import SystemMonitor
except Exception:
    SystemMonitor = None

try:
    from local.service_monitor import ServiceMonitor
except Exception:
    ServiceMonitor = None

try:
    from local.file_management import FileManager
except Exception:
    FileManager = None

try:
    from local.network_tools import NetworkTools
except Exception:
    NetworkTools = None

try:
    from remote.remote_system_monitoring import RemoteSystemMonitor
except Exception:
    RemoteSystemMonitor = None

try:
    from remote.remote_service_monitor import RemoteServiceMonitor
except Exception:
    RemoteServiceMonitor = None

try:
    from remote.remote_server_actions import RemoteServerActions
except Exception:
    RemoteServerActions = None

try:
    from security.auth_manager import AuthManager
except Exception:
    AuthManager = None

try:
    from security.audit_logger import AuditLogger
except Exception:
    AuditLogger = None

console = Console()


class ProfileManager:
    """
    Intelligent profile management with automatic library routing.
    
    ROUTING LOGIC:
    - Profile operations (create/edit/delete) → LOCAL operations
    - Profile validation → REMOTE connection test
    - Feature access → Based on connection state (LOCAL or REMOTE)
    """
    
    def __init__(self, config_manager, connection_manager=None):
        """
        Initialize Profile Manager.
        
        Args:
            config_manager: ConfigManager instance for profile storage
            connection_manager: ConnectionManager for connection testing
        """
        self.config_manager = config_manager
        self.connection_manager = connection_manager
        self.console = console
        
        # Initialize library references
        self.local_libs = self._load_local_libraries()
        self.remote_libs = self._load_remote_libraries()
        self.security_libs = self._load_security_libraries()
    
    # ============================================================
    # LIBRARY LOADING
    # ============================================================
    
    def _load_local_libraries(self) -> Dict[str, Any]:
        """Load LOCAL libraries for client-side operations."""
        libs = {}
        # Use package-qualified imports loaded at module level (fall back if unavailable)
        try:
            if SystemMonitor:
                libs['system_monitor'] = SystemMonitor()
        except Exception:
            pass

        try:
            if ServiceMonitor:
                libs['service_monitor'] = ServiceMonitor()
        except Exception:
            pass

        try:
            if FileManager:
                libs['file_manager'] = FileManager()
        except Exception:
            pass

        try:
            if NetworkTools:
                libs['network_tools'] = NetworkTools()
        except Exception:
            pass
        
        return libs
    
    def _load_remote_libraries(self) -> Dict[str, Any]:
        """Load REMOTE libraries for server-side operations."""
        libs = {}
        # Use module-level remote class references (if available)
        try:
            if RemoteSystemMonitor:
                libs['remote_monitor'] = RemoteSystemMonitor
        except Exception:
            pass

        try:
            if RemoteServiceMonitor:
                libs['remote_services'] = RemoteServiceMonitor
        except Exception:
            pass

        try:
            if RemoteServerActions:
                libs['remote_server'] = RemoteServerActions
        except Exception:
            pass
        
        return libs
    
    def _load_security_libraries(self) -> Dict[str, Any]:
        """Load SECURITY libraries for authentication/auditing."""
        libs = {}
        # Use module-level security class references (if available)
        try:
            if AuthManager:
                libs['auth_manager'] = AuthManager(self.config_manager)
        except Exception:
            pass

        try:
            if AuditLogger:
                libs['audit_logger'] = AuditLogger()
        except Exception:
            pass
        
        return libs
    
    # ============================================================
    # PROFILE CRUD OPERATIONS (LOCAL)
    # ============================================================
    
    def create_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new profile using LOCAL operations.
        
        Args:
            profile_data: Profile configuration dictionary
            
        Returns:
            Result dictionary with success status
        """
        console.print("\n[cyan]Creating profile using LOCAL operations...[/cyan]")
        
        try:
            # Validate profile data
            validation = self._validate_profile_data(profile_data)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': f"Validation failed: {validation['error']}"
                }
            
            # Check if profile name already exists
            existing = self.config_manager.get_profile(profile_data['name'])
            if existing:
                return {
                    'success': False,
                    'error': f"Profile '{profile_data['name']}' already exists"
                }
            
            # Add metadata
            profile_data['created'] = datetime.now().isoformat()
            profile_data['updated'] = datetime.now().isoformat()
            profile_data['version'] = '1.0'
            
            # Save profile using config manager (LOCAL operation)
            self.config_manager.add_profile(
                name=profile_data['name'],
                hostname=profile_data['hostname'],
                username=profile_data['username'],
                port=profile_data.get('port', 22),
                key_file=profile_data.get('key_file'),
                password=profile_data.get('password'),
                **{k: v for k, v in profile_data.items() 
                   if k not in ['name', 'hostname', 'username', 'port', 'key_file', 'password']}
            )
            
            # Log audit event (SECURITY)
            if 'audit_logger' in self.security_libs:
                self.security_libs['audit_logger'].log_event(
                    'profile_created',
                    {'profile_name': profile_data['name']}
                )
            
            console.print(f"[green]✓ Profile '{profile_data['name']}' created successfully[/green]")
            
            return {
                'success': True,
                'profile': profile_data,
                'message': 'Profile created successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to create profile: {str(e)}"
            }
    
    def read_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """
        Read profile data using LOCAL operations.
        
        Args:
            profile_name: Name of the profile to read
            
        Returns:
            Profile data dictionary or None
        """
        try:
            profile = self.config_manager.get_profile(profile_name)
            return profile
        except Exception as e:
            console.print(f"[red]Error reading profile: {e}[/red]")
            return None
    
    def update_profile(self, profile_name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update profile using LOCAL operations.
        
        Args:
            profile_name: Name of profile to update
            updates: Dictionary of fields to update
            
        Returns:
            Result dictionary with success status
        """
        console.print(f"\n[cyan]Updating profile '{profile_name}' using LOCAL operations...[/cyan]")
        
        try:
            # Get existing profile
            profile = self.config_manager.get_profile(profile_name)
            if not profile:
                return {
                    'success': False,
                    'error': f"Profile '{profile_name}' not found"
                }
            
            # Apply updates
            profile.update(updates)
            profile['updated'] = datetime.now().isoformat()
            
            # Validate updated profile
            validation = self._validate_profile_data(profile)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': f"Validation failed: {validation['error']}"
                }
            
            # Save updated profile
            self.config_manager.update_profile(profile_name, profile)
            
            # Log audit event (SECURITY)
            if 'audit_logger' in self.security_libs:
                self.security_libs['audit_logger'].log_event(
                    'profile_updated',
                    {'profile_name': profile_name, 'fields': list(updates.keys())}
                )
            
            console.print(f"[green]✓ Profile '{profile_name}' updated successfully[/green]")
            
            return {
                'success': True,
                'profile': profile,
                'message': 'Profile updated successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to update profile: {str(e)}"
            }
    
    def delete_profile(self, profile_name: str) -> Dict[str, Any]:
        """
        Delete profile using LOCAL operations.
        
        Args:
            profile_name: Name of profile to delete
            
        Returns:
            Result dictionary with success status
        """
        console.print(f"\n[cyan]Deleting profile '{profile_name}' using LOCAL operations...[/cyan]")
        
        try:
            # Check if profile exists
            profile = self.config_manager.get_profile(profile_name)
            if not profile:
                return {
                    'success': False,
                    'error': f"Profile '{profile_name}' not found"
                }
            
            # Confirm deletion
            confirm = Confirm.ask(f"[yellow]⚠️  Delete profile '{profile_name}'?[/yellow]")
            if not confirm:
                return {
                    'success': False,
                    'message': 'Deletion cancelled'
                }
            
            # Delete profile
            self.config_manager.delete_profile(profile_name)
            
            # Log audit event (SECURITY)
            if 'audit_logger' in self.security_libs:
                self.security_libs['audit_logger'].log_event(
                    'profile_deleted',
                    {'profile_name': profile_name}
                )
            
            console.print(f"[green]✓ Profile '{profile_name}' deleted successfully[/green]")
            
            return {
                'success': True,
                'message': 'Profile deleted successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to delete profile: {str(e)}"
            }
    
    def list_profiles(self, detailed: bool = False) -> List[Dict[str, Any]]:
        """
        List all profiles using LOCAL operations.
        
        Args:
            detailed: Include full profile details
            
        Returns:
            List of profile dictionaries
        """
        try:
            profiles = self.config_manager.list_profiles()
            
            if not detailed:
                # Return simplified list
                return [{
                    'name': p.get('name'),
                    'hostname': p.get('hostname'),
                    'username': p.get('username'),
                    'port': p.get('port', 22),
                } for p in profiles]
            
            return profiles
            
        except Exception as e:
            console.print(f"[red]Error listing profiles: {e}[/red]")
            return []
    
    # ============================================================
    # PROFILE VALIDATION (LOCAL + REMOTE)
    # ============================================================
    
    def _validate_profile_data(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate profile data using LOCAL checks.
        
        Args:
            profile_data: Profile data to validate
            
        Returns:
            Validation result dictionary
        """
        required_fields = ['name', 'hostname', 'username']
        
        # Check required fields
        for field in required_fields:
            if field not in profile_data or not profile_data[field]:
                return {
                    'valid': False,
                    'error': f"Missing required field: {field}"
                }
        
        # Validate port
        port = profile_data.get('port', 22)
        if not isinstance(port, int) or port < 1 or port > 65535:
            return {
                'valid': False,
                'error': f"Invalid port number: {port}"
            }
        
        # Validate authentication method
        has_key = profile_data.get('key_file')
        has_password = profile_data.get('password')
        
        if not has_key and not has_password:
            return {
                'valid': False,
                'error': "Profile must have either key_file or password"
            }
        
        return {'valid': True}
    
    def validate_profile_connection(self, profile_name: str) -> Dict[str, Any]:
        """
        Validate profile by testing connection using REMOTE libraries.
        
        Args:
            profile_name: Name of profile to validate
            
        Returns:
            Validation result dictionary
        """
        console.print(f"\n[cyan]Validating profile '{profile_name}' using REMOTE connection test...[/cyan]")
        
        if not self.connection_manager:
            return {
                'valid': False,
                'error': 'Connection manager not available'
            }
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[cyan]Testing connection..."),
                console=console
            ) as progress:
                task = progress.add_task("connect", total=None)
                
                # Create connection
                conn_id = self.connection_manager.create_connection(profile_name)
                
                # Test connection (REMOTE)
                success = self.connection_manager.connect(conn_id, timeout=10)
                
                if success:
                    # Test remote command execution
                    result = self.connection_manager.execute_command(conn_id, "echo 'test'")
                    
                    # Disconnect
                    self.connection_manager.disconnect(conn_id)
                    
                    if result.get('exit_code') == 0:
                        console.print(f"[green]✓ Profile '{profile_name}' validated successfully[/green]")
                        return {
                            'valid': True,
                            'message': 'Connection successful',
                            'latency': 'Good'
                        }
                    else:
                        return {
                            'valid': False,
                            'error': 'Command execution failed'
                        }
                else:
                    return {
                        'valid': False,
                        'error': 'Connection failed'
                    }
                    
        except Exception as e:
            return {
                'valid': False,
                'error': f"Validation failed: {str(e)}"
            }
    
    # ============================================================
    # PROFILE FEATURES (ROUTING TO LOCAL/REMOTE)
    # ============================================================
    
    def get_profile_features(self, profile_name: str, connected: bool = False) -> Dict[str, List[str]]:
        """
        Get available features for a profile based on connection state.
        Routes to LOCAL libraries when disconnected, REMOTE when connected.
        
        Args:
            profile_name: Profile name
            connected: Whether profile is currently connected
            
        Returns:
            Dictionary of available features by category
        """
        if not connected:
            # LOCAL features (available without connection)
            return {
                'profile_management': [
                    'View Profile Details',
                    'Edit Profile',
                    'Delete Profile',
                    'Validate Connection',
                    'Export Profile',
                ],
                'local_operations': [
                    'Local System Monitoring',
                    'Local File Management',
                    'Local Network Tools',
                    'Local Security Audit',
                ],
                'connection': [
                    'Connect to Device',
                    'Test Connection',
                ]
            }
        else:
            # REMOTE features (available with active connection)
            return {
                'profile_management': [
                    'View Profile Details',
                    'Edit Profile',
                    'Disconnect',
                ],
                'remote_operations': [
                    'Remote System Monitoring',
                    'Remote Service Management',
                    'Remote Server Actions',
                    'Remote File Management',
                    'Remote Process Management',
                ],
                'file_transfer': [
                    'Upload Files',
                    'Download Files',
                    'Sync Directories',
                ],
                'advanced': [
                    'Execute Commands',
                    'Interactive Shell',
                    'Port Forwarding',
                ]
            }
    
    def route_feature_to_library(self, feature_name: str, profile_name: str, 
                                 connection_id: Optional[str] = None) -> Tuple[str, Any]:
        """
        Route a feature request to the appropriate LOCAL or REMOTE library.
        
        Args:
            feature_name: Name of feature to execute
            profile_name: Profile context
            connection_id: Active connection ID (if connected)
            
        Returns:
            Tuple of (library_type, library_instance)
        """
        # Map features to libraries
        feature_routing = {
            # LOCAL features
            'Local System Monitoring': ('local', 'system_monitor'),
            'Local File Management': ('local', 'file_manager'),
            'Local Network Tools': ('local', 'network_tools'),
            'Local Service Monitor': ('local', 'service_monitor'),
            'Local Security Audit': ('local', 'security_audit'),
            
            # REMOTE features (require connection)
            'Remote System Monitoring': ('remote', 'remote_monitor'),
            'Remote Service Management': ('remote', 'remote_services'),
            'Remote Server Actions': ('remote', 'remote_server'),
            'Remote File Management': ('remote', 'remote_files'),
            'Remote Process Management': ('remote', 'remote_processes'),
            
            # SECURITY features (both)
            'SSH Key Management': ('security', 'auth_manager'),
            'Activity Logs': ('security', 'audit_logger'),
            'Device Whitelist': ('security', 'device_whitelist'),
        }
        
        if feature_name not in feature_routing:
            return ('unknown', None)
        
        lib_type, lib_key = feature_routing[feature_name]
        
        if lib_type == 'local':
            return ('local', self.local_libs.get(lib_key))
        elif lib_type == 'remote':
            if not connection_id:
                console.print("[yellow]⚠️  Remote feature requires active connection[/yellow]")
                return ('remote', None)
            
            # Get remote library class and instantiate with connection
            lib_class = self.remote_libs.get(lib_key)
            if lib_class:
                if connection_id and self.connection_manager:
                    ssh_conn = self.connection_manager.get_connection(connection_id)
                    if ssh_conn and ssh_conn.client:
                        # Instantiate remote library with SSH connection
                        lib_instance = lib_class()
                        lib_instance.set_connection(ssh_conn.client, {
                            'host': ssh_conn.profile.get('hostname'),
                            'username': ssh_conn.profile.get('username'),
                        })
                        return ('remote', lib_instance)
            return ('remote', None)
        elif lib_type == 'security':
            return ('security', self.security_libs.get(lib_key))
        
        return ('unknown', None)
    
    # ============================================================
    # PROFILE HEALTH & DIAGNOSTICS (LOCAL + REMOTE)
    # ============================================================
    
    def check_profile_health(self, profile_name: str) -> Dict[str, Any]:
        """
        Comprehensive profile health check using LOCAL and REMOTE libraries.
        
        Args:
            profile_name: Profile to check
            
        Returns:
            Health report dictionary
        """
        console.print(f"\n[cyan]Checking health of profile '{profile_name}'...[/cyan]\n")
        
        health_report = {
            'profile_name': profile_name,
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'overall_health': 'unknown'
        }
        
        # Check 1: Profile exists (LOCAL)
        profile = self.read_profile(profile_name)
        health_report['checks']['profile_exists'] = {
            'status': 'pass' if profile else 'fail',
            'library': 'LOCAL'
        }
        
        if not profile:
            health_report['overall_health'] = 'fail'
            return health_report
        
        # Check 2: Profile validation (LOCAL)
        validation = self._validate_profile_data(profile)
        health_report['checks']['profile_valid'] = {
            'status': 'pass' if validation['valid'] else 'fail',
            'library': 'LOCAL',
            'details': validation.get('error', '')
        }
        
        # Check 3: SSH key exists (LOCAL + SECURITY)
        if profile.get('key_file'):
            key_exists = Path(profile['key_file']).exists()
            health_report['checks']['ssh_key'] = {
                'status': 'pass' if key_exists else 'fail',
                'library': 'LOCAL/SECURITY',
                'details': profile['key_file']
            }
        
        # Check 4: Network connectivity (LOCAL)
        if 'network_tools' in self.local_libs:
            try:
                ping_result = self.local_libs['network_tools'].ping(profile['hostname'])
                health_report['checks']['network_connectivity'] = {
                    'status': 'pass' if ping_result else 'fail',
                    'library': 'LOCAL/network_tools'
                }
            except:
                health_report['checks']['network_connectivity'] = {
                    'status': 'skip',
                    'library': 'LOCAL/network_tools'
                }
        
        # Check 5: SSH connection (REMOTE)
        connection_check = self.validate_profile_connection(profile_name)
        health_report['checks']['ssh_connection'] = {
            'status': 'pass' if connection_check['valid'] else 'fail',
            'library': 'REMOTE',
            'details': connection_check.get('error', connection_check.get('message', ''))
        }
        
        # Calculate overall health
        total_checks = len(health_report['checks'])
        passed_checks = sum(1 for c in health_report['checks'].values() 
                           if c['status'] == 'pass')
        
        if passed_checks == total_checks:
            health_report['overall_health'] = 'excellent'
        elif passed_checks >= total_checks * 0.75:
            health_report['overall_health'] = 'good'
        elif passed_checks >= total_checks * 0.5:
            health_report['overall_health'] = 'fair'
        else:
            health_report['overall_health'] = 'poor'
        
        # Display report
        self._display_health_report(health_report)
        
        return health_report
    
    def _display_health_report(self, report: Dict[str, Any]):
        """Display health report in formatted table."""
        table = Table(title=f"Health Report: {report['profile_name']}", 
                     show_header=True, header_style="bold cyan")
        
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Library", style="dim")
        table.add_column("Details", style="dim")
        
        for check_name, check_data in report['checks'].items():
            status = check_data['status']
            status_symbol = {
                'pass': '[green]✓ Pass[/green]',
                'fail': '[red]✗ Fail[/red]',
                'skip': '[yellow]⊘ Skip[/yellow]'
            }.get(status, status)
            
            table.add_row(
                check_name.replace('_', ' ').title(),
                status_symbol,
                check_data.get('library', ''),
                check_data.get('details', '')
            )
        
        console.print(table)
        
        # Overall health
        health_color = {
            'excellent': 'green',
            'good': 'cyan',
            'fair': 'yellow',
            'poor': 'red'
        }.get(report['overall_health'], 'white')
        
        console.print(f"\n[{health_color}]Overall Health: {report['overall_health'].upper()}[/{health_color}]")
    
    # ============================================================
    # PROFILE IMPORT/EXPORT (LOCAL)
    # ============================================================
    
    def export_profile(self, profile_name: str, export_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Export profile to file using LOCAL operations.
        
        Args:
            profile_name: Profile to export
            export_path: Destination path (optional)
            
        Returns:
            Result dictionary
        """
        try:
            profile = self.read_profile(profile_name)
            if not profile:
                return {
                    'success': False,
                    'error': f"Profile '{profile_name}' not found"
                }
            
            if not export_path:
                export_dir = Path.home() / ".personal-ssh-cli" / "exports"
                export_dir.mkdir(parents=True, exist_ok=True)
                export_path = export_dir / f"{profile_name}_export.json"
            
            with open(export_path, 'w') as f:
                json.dump(profile, f, indent=2)
            
            console.print(f"[green]✓ Profile exported to: {export_path}[/green]")
            
            return {
                'success': True,
                'export_path': str(export_path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Export failed: {str(e)}"
            }
    
    def import_profile(self, import_path: str) -> Dict[str, Any]:
        """
        Import profile from file using LOCAL operations.
        
        Args:
            import_path: Path to profile file
            
        Returns:
            Result dictionary
        """
        try:
            with open(import_path, 'r') as f:
                profile_data = json.load(f)
            
            # Create profile
            result = self.create_profile(profile_data)
            
            if result['success']:
                console.print(f"[green]✓ Profile '{profile_data['name']}' imported successfully[/green]")
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Import failed: {str(e)}"
            }


# ============================================================
# INTERACTIVE PROFILE MANAGEMENT UI
# ============================================================

def run_profile_manager(config_manager, connection_manager=None):
    """
    Interactive profile management interface.
    
    Args:
        config_manager: ConfigManager instance
        connection_manager: ConnectionManager instance (optional)
    """
    manager = ProfileManager(config_manager, connection_manager)
    
    while True:
        console.clear()
        console.print(Panel(
            "[bold cyan]Profile Manager[/bold cyan]\n"
            "Intelligent routing to LOCAL/REMOTE libraries",
            border_style="cyan"
        ))
        
        console.print("\n[bold]Profile Operations (LOCAL):[/bold]")
        console.print("1. List All Profiles")
        console.print("2. View Profile Details")
        console.print("3. Create New Profile")
        console.print("4. Edit Profile")
        console.print("5. Delete Profile")
        
        console.print("\n[bold]Profile Validation (LOCAL + REMOTE):[/bold]")
        console.print("6. Validate Connection")
        console.print("7. Health Check")
        
        console.print("\n[bold]Import/Export (LOCAL):[/bold]")
        console.print("8. Export Profile")
        console.print("9. Import Profile")
        
        console.print("\n0. Back")
        
        choice = Prompt.ask("\n[cyan]Select option[/cyan]", default="0")
        
        if choice == "1":
            profiles = manager.list_profiles(detailed=True)
            
            if not profiles:
                console.print("\n[yellow]No profiles found[/yellow]")
            else:
                table = Table(title="Profiles", show_header=True, header_style="bold cyan")
                table.add_column("Name", style="cyan")
                table.add_column("Hostname", style="white")
                table.add_column("Username", style="white")
                table.add_column("Port", style="dim")
                
                for p in profiles:
                    table.add_row(
                        p.get('name', ''),
                        p.get('hostname', ''),
                        p.get('username', ''),
                        str(p.get('port', 22))
                    )
                
                console.print("\n")
                console.print(table)
            
            Prompt.ask("\n[dim]Press Enter to continue[/dim]")
            
        elif choice == "2":
            profile_name = Prompt.ask("[cyan]Profile name[/cyan]")
            profile = manager.read_profile(profile_name)
            
            if profile:
                console.print(Panel(json.dumps(profile, indent=2), title=f"Profile: {profile_name}"))
            else:
                console.print(f"\n[red]Profile '{profile_name}' not found[/red]")
            
            Prompt.ask("\n[dim]Press Enter to continue[/dim]")
            
        elif choice == "6":
            profile_name = Prompt.ask("[cyan]Profile name[/cyan]")
            result = manager.validate_profile_connection(profile_name)
            Prompt.ask("\n[dim]Press Enter to continue[/dim]")
            
        elif choice == "7":
            profile_name = Prompt.ask("[cyan]Profile name[/cyan]")
            manager.check_profile_health(profile_name)
            Prompt.ask("\n[dim]Press Enter to continue[/dim]")
            
        elif choice == "0":
            break
        else:
            console.print("[yellow]Feature coming soon![/yellow]")
            Prompt.ask("\n[dim]Press Enter to continue[/dim]")
