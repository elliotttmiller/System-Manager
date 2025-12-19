"""
Connection and Transfer Monitoring

Monitors connection quality and transfer performance.
"""
import time
import psutil
from typing import Dict, Any, Optional, List
from datetime import datetime


class ConnectionMonitor:
    """Monitors SSH connection quality."""
    
    def __init__(self):
        """Initialize connection monitor."""
        self.metrics = {}
    
    def start_monitoring(self, connection_id: str):
        """Start monitoring a connection.
        
        Args:
            connection_id: Connection identifier
        """
        self.metrics[connection_id] = {
            'start_time': time.time(),
            'commands_executed': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'errors': 0,
            'latency_samples': [],
        }
    
    def stop_monitoring(self, connection_id: str):
        """Stop monitoring a connection.
        
        Args:
            connection_id: Connection identifier
        """
        if connection_id in self.metrics:
            del self.metrics[connection_id]
    
    def record_command(self, connection_id: str, latency: float, 
                      success: bool):
        """Record command execution.
        
        Args:
            connection_id: Connection identifier
            latency: Command latency in seconds
            success: Whether command succeeded
        """
        if connection_id not in self.metrics:
            return
        
        metrics = self.metrics[connection_id]
        metrics['commands_executed'] += 1
        metrics['latency_samples'].append(latency)
        
        if not success:
            metrics['errors'] += 1
        
        # Keep only last 100 latency samples
        if len(metrics['latency_samples']) > 100:
            metrics['latency_samples'] = metrics['latency_samples'][-100:]
    
    def record_transfer(self, connection_id: str, bytes_sent: int, 
                       bytes_received: int):
        """Record data transfer.
        
        Args:
            connection_id: Connection identifier
            bytes_sent: Bytes sent
            bytes_received: Bytes received
        """
        if connection_id not in self.metrics:
            return
        
        metrics = self.metrics[connection_id]
        metrics['bytes_sent'] += bytes_sent
        metrics['bytes_received'] += bytes_received
    
    def get_metrics(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection metrics.
        
        Args:
            connection_id: Connection identifier
            
        Returns:
            Metrics dictionary or None
        """
        if connection_id not in self.metrics:
            return None
        
        metrics = self.metrics[connection_id]
        
        # Calculate statistics
        latency_samples = metrics['latency_samples']
        avg_latency = sum(latency_samples) / len(latency_samples) if latency_samples else 0
        
        uptime = time.time() - metrics['start_time']
        
        return {
            'connection_id': connection_id,
            'uptime_seconds': uptime,
            'commands_executed': metrics['commands_executed'],
            'bytes_sent': metrics['bytes_sent'],
            'bytes_received': metrics['bytes_received'],
            'errors': metrics['errors'],
            'average_latency_ms': avg_latency * 1000,
            'error_rate': metrics['errors'] / max(metrics['commands_executed'], 1),
        }


class TransferMonitor:
    """Monitors file transfer performance."""
    
    def __init__(self):
        """Initialize transfer monitor."""
        self.active_transfers = {}
    
    def start_transfer(self, transfer_id: str, total_size: int):
        """Start monitoring a file transfer.
        
        Args:
            transfer_id: Transfer identifier
            total_size: Total transfer size in bytes
        """
        self.active_transfers[transfer_id] = {
            'start_time': time.time(),
            'total_size': total_size,
            'transferred': 0,
            'last_update': time.time(),
            'speed_samples': [],
        }
    
    def update_transfer(self, transfer_id: str, bytes_transferred: int):
        """Update transfer progress.
        
        Args:
            transfer_id: Transfer identifier
            bytes_transferred: Bytes transferred
        """
        if transfer_id not in self.active_transfers:
            return
        
        transfer = self.active_transfers[transfer_id]
        current_time = time.time()
        
        # Calculate speed
        time_delta = current_time - transfer['last_update']
        if time_delta > 0:
            speed = bytes_transferred / time_delta
            transfer['speed_samples'].append(speed)
            
            # Keep only last 10 samples
            if len(transfer['speed_samples']) > 10:
                transfer['speed_samples'] = transfer['speed_samples'][-10:]
        
        transfer['transferred'] = bytes_transferred
        transfer['last_update'] = current_time
    
    def complete_transfer(self, transfer_id: str):
        """Mark transfer as complete.
        
        Args:
            transfer_id: Transfer identifier
        """
        if transfer_id in self.active_transfers:
            del self.active_transfers[transfer_id]
    
    def get_transfer_stats(self, transfer_id: str) -> Optional[Dict[str, Any]]:
        """Get transfer statistics.
        
        Args:
            transfer_id: Transfer identifier
            
        Returns:
            Statistics dictionary or None
        """
        if transfer_id not in self.active_transfers:
            return None
        
        transfer = self.active_transfers[transfer_id]
        current_time = time.time()
        
        elapsed = current_time - transfer['start_time']
        progress = transfer['transferred'] / transfer['total_size'] if transfer['total_size'] > 0 else 0
        
        # Calculate average speed
        avg_speed = sum(transfer['speed_samples']) / len(transfer['speed_samples']) if transfer['speed_samples'] else 0
        
        # Estimate time remaining
        remaining_bytes = transfer['total_size'] - transfer['transferred']
        eta = remaining_bytes / avg_speed if avg_speed > 0 else 0
        
        return {
            'transfer_id': transfer_id,
            'total_size': transfer['total_size'],
            'transferred': transfer['transferred'],
            'progress_percent': progress * 100,
            'elapsed_seconds': elapsed,
            'average_speed_bps': avg_speed,
            'eta_seconds': eta,
        }


class SystemMonitor:
    """Monitors system resources."""
    
    @staticmethod
    def get_system_stats() -> Dict[str, Any]:
        """Get system resource statistics.
        
        Returns:
            System statistics dictionary
        """
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': cpu_percent,
            'memory_total_gb': memory.total / (1024**3),
            'memory_used_gb': memory.used / (1024**3),
            'memory_percent': memory.percent,
            'disk_total_gb': disk.total / (1024**3),
            'disk_used_gb': disk.used / (1024**3),
            'disk_percent': disk.percent,
        }
