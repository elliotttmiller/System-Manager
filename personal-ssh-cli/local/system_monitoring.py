"""
Local System Monitoring Module
Advanced monitoring of local system resources, performance, and health
"""

import psutil
import platform
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
import time

console = Console()


class LocalSystemMonitor:
    """Comprehensive local system monitoring"""
    
    def __init__(self):
        self.console = console
        
    def get_system_info(self):
        """Get comprehensive system information"""
        return {
            "System": platform.system(),
            "Node Name": platform.node(),
            "Release": platform.release(),
            "Version": platform.version(),
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            "CPU Cores": psutil.cpu_count(logical=False),
            "Logical CPUs": psutil.cpu_count(logical=True),
            "Total RAM": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
            "Boot Time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_cpu_usage(self):
        """Get detailed CPU usage statistics"""
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        cpu_freq = psutil.cpu_freq()
        
        return {
            "Overall": psutil.cpu_percent(interval=1),
            "Per Core": cpu_percent,
            "Current Frequency": f"{cpu_freq.current:.2f} MHz" if cpu_freq else "N/A",
            "Min Frequency": f"{cpu_freq.min:.2f} MHz" if cpu_freq else "N/A",
            "Max Frequency": f"{cpu_freq.max:.2f} MHz" if cpu_freq else "N/A"
        }
    
    def get_memory_usage(self):
        """Get detailed memory usage statistics"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "Total": f"{memory.total / (1024**3):.2f} GB",
            "Available": f"{memory.available / (1024**3):.2f} GB",
            "Used": f"{memory.used / (1024**3):.2f} GB",
            "Percentage": f"{memory.percent}%",
            "Swap Total": f"{swap.total / (1024**3):.2f} GB",
            "Swap Used": f"{swap.used / (1024**3):.2f} GB",
            "Swap Free": f"{swap.free / (1024**3):.2f} GB",
            "Swap Percentage": f"{swap.percent}%"
        }
    
    def get_disk_usage(self):
        """Get detailed disk usage for all partitions"""
        disk_info = []
        partitions = psutil.disk_partitions()
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    "Device": partition.device,
                    "Mountpoint": partition.mountpoint,
                    "File System": partition.fstype,
                    "Total": f"{usage.total / (1024**3):.2f} GB",
                    "Used": f"{usage.used / (1024**3):.2f} GB",
                    "Free": f"{usage.free / (1024**3):.2f} GB",
                    "Percentage": f"{usage.percent}%"
                })
            except PermissionError:
                continue
        
        return disk_info
    
    def get_network_stats(self):
        """Get network interface statistics"""
        net_io = psutil.net_io_counters()
        
        return {
            "Bytes Sent": f"{net_io.bytes_sent / (1024**2):.2f} MB",
            "Bytes Received": f"{net_io.bytes_recv / (1024**2):.2f} MB",
            "Packets Sent": net_io.packets_sent,
            "Packets Received": net_io.packets_recv,
            "Errors In": net_io.errin,
            "Errors Out": net_io.errout,
            "Drop In": net_io.dropin,
            "Drop Out": net_io.dropout
        }
    
    def get_running_processes(self, limit=10):
        """Get top running processes by CPU and memory usage"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by CPU usage
        processes_sorted = sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)
        return processes_sorted[:limit]
    
    def display_system_overview(self):
        """Display comprehensive system overview"""
        # System Info Table
        sys_info = self.get_system_info()
        sys_table = Table(title="System Information", style="cyan")
        sys_table.add_column("Property", style="bold yellow")
        sys_table.add_column("Value", style="green")
        
        for key, value in sys_info.items():
            sys_table.add_row(key, str(value))
        
        self.console.print(sys_table)
        self.console.print()
        
        # CPU Usage
        cpu_usage = self.get_cpu_usage()
        cpu_table = Table(title="CPU Usage", style="cyan")
        cpu_table.add_column("Metric", style="bold yellow")
        cpu_table.add_column("Value", style="green")
        
        for key, value in cpu_usage.items():
            if key == "Per Core":
                cpu_table.add_row(key, str([f"{v:.1f}%" for v in value]))
            else:
                cpu_table.add_row(key, str(value))
        
        self.console.print(cpu_table)
        self.console.print()
        
        # Memory Usage
        memory_usage = self.get_memory_usage()
        mem_table = Table(title="Memory Usage", style="cyan")
        mem_table.add_column("Metric", style="bold yellow")
        mem_table.add_column("Value", style="green")
        
        for key, value in memory_usage.items():
            mem_table.add_row(key, value)
        
        self.console.print(mem_table)
        self.console.print()
        
        # Disk Usage
        disk_usage = self.get_disk_usage()
        disk_table = Table(title="Disk Usage", style="cyan")
        disk_table.add_column("Device", style="bold yellow")
        disk_table.add_column("Mountpoint", style="cyan")
        disk_table.add_column("Total", style="green")
        disk_table.add_column("Used", style="red")
        disk_table.add_column("Free", style="green")
        disk_table.add_column("Usage %", style="magenta")
        
        for disk in disk_usage:
            disk_table.add_row(
                disk["Device"],
                disk["Mountpoint"],
                disk["Total"],
                disk["Used"],
                disk["Free"],
                disk["Percentage"]
            )
        
        self.console.print(disk_table)
        self.console.print()
        
        # Top Processes
        processes = self.get_running_processes()
        proc_table = Table(title="Top 10 Processes by CPU Usage", style="cyan")
        proc_table.add_column("PID", style="bold yellow")
        proc_table.add_column("Name", style="cyan")
        proc_table.add_column("CPU %", style="red")
        proc_table.add_column("Memory %", style="green")
        
        for proc in processes:
            proc_table.add_row(
                str(proc['pid']),
                proc['name'],
                f"{proc['cpu_percent']:.1f}%" if proc['cpu_percent'] else "0.0%",
                f"{proc['memory_percent']:.1f}%" if proc['memory_percent'] else "0.0%"
            )
        
        self.console.print(proc_table)
    
    def live_monitoring(self, duration=30):
        """Live monitoring dashboard with real-time updates"""
        self.console.print(Panel.fit(
            "[bold cyan]Live System Monitoring[/bold cyan]\n"
            f"Duration: {duration} seconds\n"
            "Press Ctrl+C to stop",
            border_style="cyan"
        ))
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                # Clear and display updated stats
                self.console.clear()
                self.display_system_overview()
                time.sleep(2)  # Update every 2 seconds
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Monitoring stopped by user[/yellow]")


def run():
    """Main entry point for local system monitoring"""
    monitor = LocalSystemMonitor()
    
    console.print(Panel.fit(
        "[bold cyan]Local System Monitoring[/bold cyan]\n"
        "Select an option:",
        border_style="cyan"
    ))
    
    options = [
        "1. System Overview",
        "2. Live Monitoring (30 seconds)",
        "3. CPU Details",
        "4. Memory Details",
        "5. Disk Details",
        "6. Network Statistics",
        "7. Top Processes",
        "0. Back to Main Menu"
    ]
    
    for option in options:
        console.print(f"  {option}")
    
    choice = console.input("\n[bold yellow]Enter your choice: [/bold yellow]")
    
    if choice == "1":
        monitor.display_system_overview()
    elif choice == "2":
        monitor.live_monitoring()
    elif choice == "3":
        cpu_usage = monitor.get_cpu_usage()
        table = Table(title="CPU Details", style="cyan")
        table.add_column("Metric", style="bold yellow")
        table.add_column("Value", style="green")
        for key, value in cpu_usage.items():
            table.add_row(key, str(value))
        console.print(table)
    elif choice == "4":
        memory_usage = monitor.get_memory_usage()
        table = Table(title="Memory Details", style="cyan")
        table.add_column("Metric", style="bold yellow")
        table.add_column("Value", style="green")
        for key, value in memory_usage.items():
            table.add_row(key, value)
        console.print(table)
    elif choice == "5":
        disk_usage = monitor.get_disk_usage()
        table = Table(title="Disk Details", style="cyan")
        table.add_column("Device", style="bold yellow")
        table.add_column("Mountpoint", style="cyan")
        table.add_column("Total", style="green")
        table.add_column("Used", style="red")
        table.add_column("Free", style="green")
        table.add_column("Usage %", style="magenta")
        for disk in disk_usage:
            table.add_row(
                disk["Device"],
                disk["Mountpoint"],
                disk["Total"],
                disk["Used"],
                disk["Free"],
                disk["Percentage"]
            )
        console.print(table)
    elif choice == "6":
        net_stats = monitor.get_network_stats()
        table = Table(title="Network Statistics", style="cyan")
        table.add_column("Metric", style="bold yellow")
        table.add_column("Value", style="green")
        for key, value in net_stats.items():
            table.add_row(key, str(value))
        console.print(table)
    elif choice == "7":
        processes = monitor.get_running_processes()
        table = Table(title="Top Processes", style="cyan")
        table.add_column("PID", style="bold yellow")
        table.add_column("Name", style="cyan")
        table.add_column("CPU %", style="red")
        table.add_column("Memory %", style="green")
        for proc in processes:
            table.add_row(
                str(proc['pid']),
                proc['name'],
                f"{proc['cpu_percent']:.1f}%" if proc['cpu_percent'] else "0.0%",
                f"{proc['memory_percent']:.1f}%" if proc['memory_percent'] else "0.0%"
            )
        console.print(table)
    
    console.input("\n[bold yellow]Press Enter to continue...[/bold yellow]")


if __name__ == "__main__":
    run()
