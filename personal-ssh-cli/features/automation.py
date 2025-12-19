"""
Automation System

Command sequences and scheduled tasks.
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class Automation:
    """Handles automation and command sequences."""
    
    def __init__(self, config_manager):
        """Initialize automation system.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config_manager = config_manager
        self.macros_file = config_manager.config_dir / "macros.json"
        self.macros = self._load_macros()
    
    def _load_macros(self) -> Dict[str, Any]:
        """Load macros from file."""
        if not self.macros_file.exists():
            return {}
        
        try:
            with open(self.macros_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_macros(self):
        """Save macros to file."""
        with open(self.macros_file, 'w') as f:
            json.dump(self.macros, f, indent=2)
    
    def create_macro(self, name: str, commands: List[str], 
                    description: Optional[str] = None):
        """Create command macro.
        
        Args:
            name: Macro name
            commands: List of commands
            description: Optional description
        """
        self.macros[name] = {
            'commands': commands,
            'description': description or '',
            'created_at': datetime.now().isoformat(),
        }
        self._save_macros()
    
    def delete_macro(self, name: str) -> bool:
        """Delete macro.
        
        Args:
            name: Macro name
            
        Returns:
            True if deleted
        """
        if name in self.macros:
            del self.macros[name]
            self._save_macros()
            return True
        return False
    
    def get_macro(self, name: str) -> Optional[Dict[str, Any]]:
        """Get macro by name.
        
        Args:
            name: Macro name
            
        Returns:
            Macro definition or None
        """
        return self.macros.get(name)
    
    def list_macros(self) -> List[Dict[str, Any]]:
        """List all macros.
        
        Returns:
            List of macro information
        """
        return [
            {
                'name': name,
                'description': macro['description'],
                'commands_count': len(macro['commands']),
                'created_at': macro['created_at'],
            }
            for name, macro in self.macros.items()
        ]
    
    def execute_macro(self, name: str, connection_manager, 
                     connection_id: str) -> List[Dict[str, Any]]:
        """Execute macro commands.
        
        Args:
            name: Macro name
            connection_manager: ConnectionManager instance
            connection_id: Connection to execute on
            
        Returns:
            List of command results
        """
        macro = self.get_macro(name)
        if not macro:
            raise ValueError(f"Macro '{name}' not found")
        
        results = []
        for command in macro['commands']:
            result = connection_manager.execute_command(connection_id, command)
            results.append({
                'command': command,
                'result': result,
            })
        
        return results
