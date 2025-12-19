"""
Session Manager

Tracks active sessions and handles session persistence and recovery.
"""
import json
import time
from pathlib import Path
from typing import Dict, Optional, Any, List
from datetime import datetime


class Session:
    """Represents a command session."""
    
    def __init__(self, session_id: str, connection_id: str, profile_name: str):
        """Initialize session.
        
        Args:
            session_id: Unique session identifier
            connection_id: Associated connection ID
            profile_name: Device profile name
        """
        self.session_id = session_id
        self.connection_id = connection_id
        self.profile_name = profile_name
        self.created_at = time.time()
        self.last_activity = time.time()
        self.working_directory = "~"
        self.environment = {}
        self.command_history = []
        self.state = "active"  # active, background, suspended
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary.
        
        Returns:
            Session data dictionary
        """
        return {
            'session_id': self.session_id,
            'connection_id': self.connection_id,
            'profile_name': self.profile_name,
            'created_at': self.created_at,
            'last_activity': self.last_activity,
            'working_directory': self.working_directory,
            'environment': self.environment,
            'command_history': self.command_history[-100:],  # Keep last 100 commands
            'state': self.state,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Create session from dictionary.
        
        Args:
            data: Session data dictionary
            
        Returns:
            Session instance
        """
        session = cls(
            data['session_id'],
            data['connection_id'],
            data['profile_name']
        )
        session.created_at = data.get('created_at', time.time())
        session.last_activity = data.get('last_activity', time.time())
        session.working_directory = data.get('working_directory', '~')
        session.environment = data.get('environment', {})
        session.command_history = data.get('command_history', [])
        session.state = data.get('state', 'active')
        return session
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = time.time()
    
    def add_command(self, command: str):
        """Add command to history.
        
        Args:
            command: Command string
        """
        self.command_history.append({
            'command': command,
            'timestamp': time.time(),
        })
        self.update_activity()


class SessionManager:
    """Manages sessions with persistence and recovery."""
    
    def __init__(self, config_manager):
        """Initialize session manager.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config_manager = config_manager
        self.sessions: Dict[str, Session] = {}
        self.sessions_file = config_manager.config_dir / "sessions.json"
        self._next_id = 1
        
        # Load existing sessions
        self._load_sessions()
    
    def create_session(self, connection_id: str, profile_name: str,
                      session_id: Optional[str] = None) -> str:
        """Create new session.
        
        Args:
            connection_id: Connection identifier
            profile_name: Device profile name
            session_id: Optional custom session ID
            
        Returns:
            Session ID
        """
        if session_id is None:
            session_id = f"session_{self._next_id}"
            self._next_id += 1
        
        session = Session(session_id, connection_id, profile_name)
        self.sessions[session_id] = session
        
        self._save_sessions()
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session or None if not found
        """
        return self.sessions.get(session_id)
    
    def list_sessions(self, state: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all sessions.
        
        Args:
            state: Optional state filter (active, background, suspended)
            
        Returns:
            List of session information dictionaries
        """
        result = []
        for session in self.sessions.values():
            if state is None or session.state == state:
                result.append({
                    'session_id': session.session_id,
                    'connection_id': session.connection_id,
                    'profile_name': session.profile_name,
                    'state': session.state,
                    'created_at': datetime.fromtimestamp(session.created_at).isoformat(),
                    'last_activity': datetime.fromtimestamp(session.last_activity).isoformat(),
                    'working_directory': session.working_directory,
                    'commands_count': len(session.command_history),
                })
        return result
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_sessions()
            return True
        return False
    
    def update_session_state(self, session_id: str, state: str):
        """Update session state.
        
        Args:
            session_id: Session identifier
            state: New state (active, background, suspended)
        """
        session = self.sessions.get(session_id)
        if session:
            session.state = state
            session.update_activity()
            self._save_sessions()
    
    def add_command_to_session(self, session_id: str, command: str):
        """Add command to session history.
        
        Args:
            session_id: Session identifier
            command: Command string
        """
        session = self.sessions.get(session_id)
        if session:
            session.add_command(command)
            self._save_sessions()
    
    def update_working_directory(self, session_id: str, directory: str):
        """Update session working directory.
        
        Args:
            session_id: Session identifier
            directory: New working directory
        """
        session = self.sessions.get(session_id)
        if session:
            session.working_directory = directory
            session.update_activity()
            self._save_sessions()
    
    def get_session_history(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get session command history.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of commands to return
            
        Returns:
            List of command history entries
        """
        session = self.sessions.get(session_id)
        if not session:
            return []
        
        return session.command_history[-limit:]
    
    def cleanup_old_sessions(self, max_age_hours: int = 168):
        """Remove old sessions (default: 7 days).
        
        Args:
            max_age_hours: Maximum age in hours
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        old_sessions = [
            session_id for session_id, session in self.sessions.items()
            if current_time - session.last_activity > max_age_seconds
        ]
        
        for session_id in old_sessions:
            del self.sessions[session_id]
        
        if old_sessions:
            self._save_sessions()
    
    def _save_sessions(self):
        """Save sessions to persistent storage."""
        if not self.config_manager.get_setting('settings.auto_save_sessions', True):
            return
        
        data = {
            'sessions': {
                session_id: session.to_dict()
                for session_id, session in self.sessions.items()
            },
            'next_id': self._next_id,
        }
        
        with open(self.sessions_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_sessions(self):
        """Load sessions from persistent storage."""
        if not self.sessions_file.exists():
            return
        
        try:
            with open(self.sessions_file, 'r') as f:
                data = json.load(f)
            
            for session_id, session_data in data.get('sessions', {}).items():
                self.sessions[session_id] = Session.from_dict(session_data)
            
            self._next_id = data.get('next_id', 1)
            
        except Exception:
            # If loading fails, start fresh
            pass
