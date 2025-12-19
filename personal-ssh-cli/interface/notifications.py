"""
System Notifications

Handles system notifications and alerts.
"""
import platform
from typing import Optional


class NotificationSystem:
    """System notification handler."""
    
    def __init__(self):
        """Initialize notification system."""
        self.system = platform.system()
        self.notifications_enabled = True
    
    def send_notification(self, title: str, message: str, 
                         urgency: str = "normal"):
        """Send system notification.
        
        Args:
            title: Notification title
            message: Notification message
            urgency: Urgency level (low, normal, critical)
        """
        if not self.notifications_enabled:
            return
        
        try:
            if self.system == "Windows":
                self._send_windows_notification(title, message)
            elif self.system == "Darwin":  # macOS
                self._send_macos_notification(title, message)
            elif self.system == "Linux":
                self._send_linux_notification(title, message, urgency)
        except Exception:
            # Silently fail if notifications are not available
            pass
    
    def _send_windows_notification(self, title: str, message: str):
        """Send Windows notification."""
        try:
            from winotify import Notification
            toast = Notification(
                app_id="Personal SSH CLI",
                title=title,
                msg=message
            )
            toast.show()
        except ImportError:
            pass
    
    def _send_macos_notification(self, title: str, message: str):
        """Send macOS notification."""
        import subprocess
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(['osascript', '-e', script], 
                      capture_output=True, check=False)
    
    def _send_linux_notification(self, title: str, message: str, 
                                urgency: str):
        """Send Linux notification."""
        import subprocess
        subprocess.run(['notify-send', '-u', urgency, title, message],
                      capture_output=True, check=False)
    
    def enable(self):
        """Enable notifications."""
        self.notifications_enabled = True
    
    def disable(self):
        """Disable notifications."""
        self.notifications_enabled = False
