"""
Tab Completion System

Provides autocomplete functionality for commands and parameters.
"""
from typing import List, Optional


class AutoComplete:
    """Tab completion system for CLI."""
    
    def __init__(self, config_manager):
        """Initialize autocomplete.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config_manager = config_manager
    
    def complete_profile_name(self, prefix: str = "") -> List[str]:
        """Complete profile names.
        
        Args:
            prefix: Partial profile name
            
        Returns:
            List of matching profile names
        """
        profiles = self.config_manager.list_profiles()
        
        if not prefix:
            return profiles
        
        return [p for p in profiles if p.startswith(prefix)]
    
    def complete_connection_id(self, connection_manager, prefix: str = "") -> List[str]:
        """Complete connection IDs.
        
        Args:
            connection_manager: ConnectionManager instance
            prefix: Partial connection ID
            
        Returns:
            List of matching connection IDs
        """
        connections = connection_manager.list_connections()
        conn_ids = [c['id'] for c in connections]
        
        if not prefix:
            return conn_ids
        
        return [cid for cid in conn_ids if cid.startswith(prefix)]
    
    def complete_session_id(self, session_manager, prefix: str = "") -> List[str]:
        """Complete session IDs.
        
        Args:
            session_manager: SessionManager instance
            prefix: Partial session ID
            
        Returns:
            List of matching session IDs
        """
        sessions = session_manager.list_sessions()
        session_ids = [s['session_id'] for s in sessions]
        
        if not prefix:
            return session_ids
        
        return [sid for sid in session_ids if sid.startswith(prefix)]
    
    def complete_command(self, prefix: str = "") -> List[str]:
        """Complete command names.
        
        Args:
            prefix: Partial command name
            
        Returns:
            List of matching commands
        """
        commands = [
            'connect', 'disconnect', 'exec', 'upload', 'download',
            'list-connections', 'list-profiles', 'list-sessions',
            'add-profile', 'delete-profile', 'setup', 'version',
        ]
        
        if not prefix:
            return commands
        
        return [cmd for cmd in commands if cmd.startswith(prefix)]
