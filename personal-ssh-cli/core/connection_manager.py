"""
Connection Manager for SSH Sessions

Handles SSH connection lifecycle, session management, and multiplexing.
"""
import time
import paramiko
from typing import Dict, Optional, Any, List
from pathlib import Path
import threading
import queue


class SSHConnection:
    """Represents a single SSH connection."""
    
    def __init__(self, profile: Dict[str, Any], connection_id: str):
        """Initialize SSH connection.
        
        Args:
            profile: Device profile configuration
            connection_id: Unique connection identifier
        """
        self.profile = profile
        self.connection_id = connection_id
        self.client: Optional[paramiko.SSHClient] = None
        self.connected = False
        self.last_activity = time.time()
        self.working_directory = "~"
        self.environment = {}
        
    def connect(self, timeout: int = 30) -> bool:
        """Establish SSH connection.
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            True if connection successful
        """
        try:
            self.client = paramiko.SSHClient()
            
            # Load host keys
            host_keys_file = Path.home() / ".ssh" / "known_hosts"
            if host_keys_file.exists():
                self.client.load_host_keys(str(host_keys_file))
            
            # Set host key policy based on profile
            if self.profile.get('verify_host_keys', True):
                self.client.set_missing_host_key_policy(paramiko.RejectPolicy())
            else:
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connection parameters
            connect_params = {
                'hostname': self.profile['hostname'],
                'port': self.profile.get('port', 22),
                'username': self.profile['username'],
                'timeout': timeout,
                'compress': self.profile.get('compression', True),
            }
            
            # Authentication
            if 'key_file' in self.profile:
                connect_params['key_filename'] = self.profile['key_file']
            elif 'password' in self.profile:
                connect_params['password'] = self.profile['password']
            
            # Connect
            self.client.connect(**connect_params)
            self.connected = True
            self.last_activity = time.time()
            
            return True
            
        except Exception as e:
            self.connected = False
            raise ConnectionError(f"Failed to connect: {str(e)}")
    
    def disconnect(self):
        """Close SSH connection."""
        if self.client:
            self.client.close()
            self.connected = False
    
    def execute_command(self, command: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Execute command on remote system.
        
        Args:
            command: Command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Dictionary with stdout, stderr, and exit_code
        """
        if not self.connected or not self.client:
            raise RuntimeError("Not connected")
        
        self.last_activity = time.time()
        
        stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
        
        return {
            'stdout': stdout.read().decode('utf-8', errors='replace'),
            'stderr': stderr.read().decode('utf-8', errors='replace'),
            'exit_code': stdout.channel.recv_exit_status()
        }
    
    def is_alive(self) -> bool:
        """Check if connection is still alive.
        
        Returns:
            True if connection is active
        """
        if not self.connected or not self.client:
            return False
        
        try:
            transport = self.client.get_transport()
            if transport and transport.is_active():
                return True
        except Exception:
            pass
        
        return False
    
    def get_sftp_client(self):
        """Get SFTP client for file operations.
        
        Returns:
            paramiko.SFTPClient instance
        """
        if not self.connected or not self.client:
            raise RuntimeError("Not connected")
        
        return self.client.open_sftp()


class ConnectionManager:
    """Manages multiple SSH connections and sessions."""
    
    def __init__(self, config_manager):
        """Initialize connection manager.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config_manager = config_manager
        self.connections: Dict[str, SSHConnection] = {}
        self._connection_lock = threading.Lock()
        self._next_id = 1
        
    def create_connection(self, profile_name: str, connection_id: Optional[str] = None) -> str:
        """Create new SSH connection.
        
        Args:
            profile_name: Name of device profile to use
            connection_id: Optional custom connection ID
            
        Returns:
            Connection ID
        """
        profile = self.config_manager.get_profile(profile_name)
        if not profile:
            raise ValueError(f"Profile '{profile_name}' not found")
        
        with self._connection_lock:
            if connection_id is None:
                connection_id = f"conn_{self._next_id}"
                self._next_id += 1
            
            connection = SSHConnection(profile, connection_id)
            self.connections[connection_id] = connection
        
        return connection_id
    
    def connect(self, connection_id: str, timeout: int = 30) -> Optional[SSHConnection]:
        """Establish SSH connection and return the connection object.
        
        Args:
            connection_id: Connection identifier
            timeout: Connection timeout in seconds
            
        Returns:
            SSHConnection object if connection is successful
        """
        connection = self.connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection '{connection_id}' not found")
        
        if connection.connect(timeout=timeout):
            return connection
        return None
    
    def disconnect(self, connection_id: str):
        """Close SSH connection.
        
        Args:
            connection_id: Connection identifier
        """
        connection = self.connections.get(connection_id)
        if connection:
            connection.disconnect()
    
    def disconnect_all(self):
        """Close all active connections."""
        with self._connection_lock:
            for connection in self.connections.values():
                connection.disconnect()
            self.connections.clear()
    
    def execute_command(self, connection_id: str, command: str, 
                       timeout: Optional[int] = None) -> Dict[str, Any]:
        """Execute command on connection.
        
        Args:
            connection_id: Connection identifier
            command: Command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Dictionary with command results
        """
        connection = self.connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection '{connection_id}' not found")
        
        return connection.execute_command(command, timeout=timeout)
    
    def get_connection(self, connection_id: str) -> Optional[SSHConnection]:
        """Get connection by ID.
        
        Args:
            connection_id: Connection identifier
            
        Returns:
            SSHConnection or None
        """
        return self.connections.get(connection_id)
    
    def list_connections(self) -> List[Dict[str, Any]]:
        """List all connections with status.
        
        Returns:
            List of connection information dictionaries
        """
        result = []
        with self._connection_lock:
            for conn_id, conn in self.connections.items():
                result.append({
                    'id': conn_id,
                    'hostname': conn.profile.get('hostname'),
                    'username': conn.profile.get('username'),
                    'connected': conn.connected,
                    'alive': conn.is_alive(),
                    'last_activity': conn.last_activity,
                    'working_directory': conn.working_directory,
                })
        return result
    
    def reconnect(self, connection_id: str, timeout: int = 30) -> bool:
        """Reconnect an existing connection.
        
        Args:
            connection_id: Connection identifier
            timeout: Connection timeout in seconds
            
        Returns:
            True if reconnection successful
        """
        connection = self.connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection '{connection_id}' not found")
        
        if connection.connected:
            connection.disconnect()
        
        return connection.connect(timeout=timeout)
    
    def cleanup_dead_connections(self):
        """Remove connections that are no longer alive."""
        with self._connection_lock:
            dead_connections = [
                conn_id for conn_id, conn in self.connections.items()
                if not conn.is_alive()
            ]
            
            for conn_id in dead_connections:
                self.connections[conn_id].disconnect()
                del self.connections[conn_id]
