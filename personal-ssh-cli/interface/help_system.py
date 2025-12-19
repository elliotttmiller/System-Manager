"""
Context-Aware Help System

Provides contextual help and examples for commands.
"""
from typing import Dict, List, Optional


class HelpSystem:
    """Context-aware help system."""
    
    def __init__(self):
        """Initialize help system."""
        self.help_topics = self._initialize_help_topics()
        self.examples = self._initialize_examples()
    
    def _initialize_help_topics(self) -> Dict[str, str]:
        """Initialize help topic content."""
        return {
            'connect': """
## Connect to a Device

Connect to a remote device using a saved profile.

### Usage
    pssh connect <profile-name>

### Options
    profile-name    Name of the device profile to connect to

### Examples
    pssh connect home-server
    pssh connect work-laptop
    pssh connect raspberry-pi

### See Also
    - list-profiles: View all saved profiles
    - add-profile: Create a new device profile
""",
            'upload': """
## Upload Files

Upload files or directories to a remote system.

### Usage
    pssh upload <connection-id> <local-path> <remote-path> [options]

### Options
    --verify/--no-verify    Verify file integrity (default: verify)

### Examples
    # Upload a single file
    pssh upload conn_1 /home/user/document.pdf ~/documents/

    # Upload without verification (faster)
    pssh upload conn_1 ./file.txt /tmp/ --no-verify

### See Also
    - download: Download files from remote system
    - list-connections: View active connections
""",
            'profiles': """
## Device Profiles

Device profiles store connection information for your devices.

### Managing Profiles
    # Add new profile
    pssh add-profile <name> --hostname <host> --username <user>

    # List all profiles
    pssh list-profiles

    # Delete profile
    pssh delete-profile <name>

### Profile Configuration
Profiles can include:
    - Hostname or IP address
    - SSH username
    - Port number (default: 22)
    - SSH key file path
    - Connection options

### Examples
    # Add profile with SSH key
    pssh add-profile server --hostname 192.168.1.100 --username admin --key-file ~/.ssh/id_ed25519

    # Add profile with custom port
    pssh add-profile custom --hostname example.com --username user --port 2222
""",
        }
    
    def _initialize_examples(self) -> Dict[str, List[str]]:
        """Initialize command examples."""
        return {
            'quick_start': [
                '# Set up the system',
                'pssh setup',
                '',
                '# Add your first device',
                'pssh add-profile home-server --hostname 192.168.1.100 --username user',
                '',
                '# Connect to the device',
                'pssh connect home-server',
                '',
                '# Upload a file',
                'pssh upload conn_1 /local/file.txt /remote/file.txt',
            ],
            'common_tasks': [
                '# List all connections',
                'pssh list-connections',
                '',
                '# Execute a command',
                'pssh exec conn_1 "ls -la"',
                '',
                '# Download a file',
                'pssh download conn_1 /remote/log.txt ./local/log.txt',
                '',
                '# View sessions',
                'pssh list-sessions',
            ],
        }
    
    def get_help(self, topic: str) -> Optional[str]:
        """Get help for a specific topic.
        
        Args:
            topic: Help topic name
            
        Returns:
            Help content or None if not found
        """
        return self.help_topics.get(topic)
    
    def get_examples(self, category: str) -> List[str]:
        """Get examples for a category.
        
        Args:
            category: Example category
            
        Returns:
            List of example commands
        """
        return self.examples.get(category, [])
    
    def search_help(self, query: str) -> List[str]:
        """Search help topics.
        
        Args:
            query: Search query
            
        Returns:
            List of matching topic names
        """
        query_lower = query.lower()
        matches = []
        
        for topic, content in self.help_topics.items():
            if query_lower in topic.lower() or query_lower in content.lower():
                matches.append(topic)
        
        return matches
    
    def list_topics(self) -> List[str]:
        """List all help topics.
        
        Returns:
            List of topic names
        """
        return list(self.help_topics.keys())
