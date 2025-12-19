"""
Audit Logger

Local activity logging for security and troubleshooting.
"""
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class AuditLogger:
    """Logs system activities for audit purposes."""
    
    def __init__(self, config_manager):
        """Initialize audit logger.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config_manager = config_manager
        self.log_dir = config_manager.config_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.log_file = self.log_dir / "audit.log"
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration.
        
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger('personal_ssh_audit')
        logger.setLevel(logging.INFO)
        
        # File handler with rotation
        handler = logging.FileHandler(self.log_file)
        handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        
        return logger
    
    def log_connection(self, profile_name: str, hostname: str, 
                      username: str, success: bool):
        """Log connection attempt.
        
        Args:
            profile_name: Device profile name
            hostname: Target hostname
            username: SSH username
            success: Whether connection was successful
        """
        event = {
            'event_type': 'connection',
            'profile': profile_name,
            'hostname': hostname,
            'username': username,
            'success': success,
            'timestamp': datetime.now().isoformat(),
        }
        
        self.logger.info(json.dumps(event))
    
    def log_command(self, connection_id: str, command: str, 
                   exit_code: int):
        """Log command execution.
        
        Args:
            connection_id: Connection identifier
            command: Executed command
            exit_code: Command exit code
        """
        event = {
            'event_type': 'command',
            'connection_id': connection_id,
            'command': command,
            'exit_code': exit_code,
            'timestamp': datetime.now().isoformat(),
        }
        
        self.logger.info(json.dumps(event))
    
    def log_file_transfer(self, transfer_type: str, local_path: str,
                         remote_path: str, size: int, success: bool):
        """Log file transfer.
        
        Args:
            transfer_type: 'upload' or 'download'
            local_path: Local file path
            remote_path: Remote file path
            size: File size in bytes
            success: Whether transfer was successful
        """
        event = {
            'event_type': 'file_transfer',
            'transfer_type': transfer_type,
            'local_path': local_path,
            'remote_path': remote_path,
            'size': size,
            'success': success,
            'timestamp': datetime.now().isoformat(),
        }
        
        self.logger.info(json.dumps(event))
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related event.
        
        Args:
            event_type: Type of security event
            details: Event details
        """
        event = {
            'event_type': 'security',
            'security_event': event_type,
            'details': details,
            'timestamp': datetime.now().isoformat(),
        }
        
        self.logger.warning(json.dumps(event))
    
    def log_error(self, error_type: str, message: str, 
                 context: Optional[Dict[str, Any]] = None):
        """Log error event.
        
        Args:
            error_type: Type of error
            message: Error message
            context: Optional context information
        """
        event = {
            'event_type': 'error',
            'error_type': error_type,
            'message': message,
            'context': context or {},
            'timestamp': datetime.now().isoformat(),
        }
        
        self.logger.error(json.dumps(event))
    
    def get_recent_logs(self, count: int = 100) -> list:
        """Get recent log entries.
        
        Args:
            count: Number of entries to retrieve
            
        Returns:
            List of log entries
        """
        if not self.log_file.exists():
            return []
        
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
            
            # Return last N lines
            return [line.strip() for line in lines[-count:]]
            
        except Exception:
            return []
