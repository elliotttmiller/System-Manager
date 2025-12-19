"""
Local Automation Module
Task automation, scripting, and scheduled job management
"""

import os
import subprocess
import platform
import json
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

console = Console()


class LocalAutomation:
    """Comprehensive local automation and scripting tools"""
    
    def __init__(self):
        self.console = console
        self.system = platform.system()
        self.automation_dir = Path.home() / ".system-manager" / "automation"
        self.automation_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_file = self.automation_dir / "tasks.json"
    
    def load_tasks(self):
        """Load saved automation tasks"""
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_tasks(self, tasks):
        """Save automation tasks"""
        with open(self.tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
    
    def create_task(self, name, command, schedule=None, description=""):
        """Create a new automation task"""
        tasks = self.load_tasks()
        
        task = {
            "id": len(tasks) + 1,
            "name": name,
            "command": command,
            "schedule": schedule,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "last_run": None,
            "status": "active"
        }
        
        tasks.append(task)
        self.save_tasks(tasks)
        
        return task
    
    def list_tasks(self):
        """List all automation tasks"""
        return self.load_tasks()
    
    def delete_task(self, task_id):
        """Delete an automation task"""
        tasks = self.load_tasks()
        tasks = [t for t in tasks if t['id'] != task_id]
        self.save_tasks(tasks)
        return True
    
    def run_task(self, task_id):
        """Execute a specific task"""
        tasks = self.load_tasks()
        task = next((t for t in tasks if t['id'] == task_id), None)
        
        if not task:
            return {"status": "error", "message": "Task not found"}
        
        try:
            result = subprocess.run(
                task['command'],
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Update last run time
            task['last_run'] = datetime.now().isoformat()
            self.save_tasks(tasks)
            
            return {
                "status": "success",
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Task execution timeout"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def create_scheduled_task(self, name, command, schedule_type, schedule_value):
        """Create a scheduled task using OS scheduler"""
        try:
            if self.system == "Windows":
                # Use Windows Task Scheduler
                if schedule_type == "daily":
                    schtasks_cmd = [
                        'schtasks', '/create',
                        '/tn', name,
                        '/tr', command,
                        '/sc', 'daily',
                        '/st', schedule_value,  # Time in HH:MM format
                        '/f'
                    ]
                elif schedule_type == "hourly":
                    schtasks_cmd = [
                        'schtasks', '/create',
                        '/tn', name,
                        '/tr', command,
                        '/sc', 'hourly',
                        '/mo', schedule_value,  # Every N hours
                        '/f'
                    ]
                else:
                    return {"status": "error", "message": "Unsupported schedule type"}
                
                result = subprocess.run(schtasks_cmd, capture_output=True, text=True)
                return {"status": "success", "output": result.stdout}
            
            elif self.system == "Linux":
                # Use cron
                cron_schedule = self._convert_to_cron(schedule_type, schedule_value)
                cron_entry = f"{cron_schedule} {command}\n"
                
                # Add to crontab
                result = subprocess.run(
                    ['crontab', '-l'],
                    capture_output=True,
                    text=True
                )
                
                current_crontab = result.stdout if result.returncode == 0 else ""
                new_crontab = current_crontab + cron_entry
                
                # Write back to crontab
                process = subprocess.Popen(
                    ['crontab', '-'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate(input=new_crontab)
                
                return {"status": "success", "output": "Cron job created"}
            
            else:
                return {"status": "error", "message": "Unsupported OS"}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _convert_to_cron(self, schedule_type, schedule_value):
        """Convert schedule to cron format"""
        if schedule_type == "daily":
            # schedule_value should be time like "14:30"
            hour, minute = schedule_value.split(':')
            return f"{minute} {hour} * * *"
        elif schedule_type == "hourly":
            # schedule_value is number of hours
            return f"0 */{schedule_value} * * *"
        elif schedule_type == "weekly":
            # schedule_value could be "Monday 14:30"
            day_map = {
                'Monday': '1', 'Tuesday': '2', 'Wednesday': '3',
                'Thursday': '4', 'Friday': '5', 'Saturday': '6', 'Sunday': '0'
            }
            parts = schedule_value.split()
            day = day_map.get(parts[0], '1')
            time_parts = parts[1].split(':')
            return f"{time_parts[1]} {time_parts[0]} * * {day}"
        else:
            return "0 0 * * *"  # Default: daily at midnight
    
    def list_scheduled_tasks(self):
        """List all scheduled tasks from OS scheduler"""
        try:
            if self.system == "Windows":
                result = subprocess.run(
                    ['schtasks', '/query', '/fo', 'csv'],
                    capture_output=True,
                    text=True
                )
                return {"status": "success", "output": result.stdout}
            
            elif self.system == "Linux":
                result = subprocess.run(
                    ['crontab', '-l'],
                    capture_output=True,
                    text=True
                )
                return {"status": "success", "output": result.stdout}
            
            else:
                return {"status": "error", "message": "Unsupported OS"}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def create_batch_script(self, name, commands):
        """Create a batch script file"""
        extension = ".bat" if self.system == "Windows" else ".sh"
        script_path = self.automation_dir / f"{name}{extension}"
        
        try:
            with open(script_path, 'w') as f:
                if self.system == "Windows":
                    f.write("@echo off\n")
                    f.write("\n".join(commands))
                else:
                    f.write("#!/bin/bash\n")
                    f.write("\n".join(commands))
            
            # Make executable on Unix
            if self.system != "Windows":
                os.chmod(script_path, 0o755)
            
            return {
                "status": "success",
                "path": str(script_path),
                "message": f"Script created at {script_path}"
            }
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def execute_batch_script(self, script_path):
        """Execute a batch script"""
        try:
            if self.system == "Windows":
                result = subprocess.run(
                    ['cmd', '/c', script_path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            else:
                result = subprocess.run(
                    ['bash', script_path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            
            return {
                "status": "success",
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
        
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Script execution timeout"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


def run():
    """Main entry point for local automation"""
    automation = LocalAutomation()
    
    console.print(Panel.fit(
        "[bold cyan]Local Automation[/bold cyan]\n"
        "Task automation and scripting tools",
        border_style="cyan"
    ))
    
    options = [
        "1. List Automation Tasks",
        "2. Create New Task",
        "3. Run Task",
        "4. Delete Task",
        "5. Create Scheduled Task",
        "6. List Scheduled Tasks",
        "7. Create Batch Script",
        "8. Execute Batch Script",
        "0. Back to Main Menu"
    ]
    
    for option in options:
        console.print(f"  {option}")
    
    choice = console.input("\n[bold yellow]Enter your choice: [/bold yellow]")
    
    if choice == "1":
        tasks = automation.list_tasks()
        
        if tasks:
            table = Table(title=f"Automation Tasks ({len(tasks)})", style="cyan")
            table.add_column("ID", style="bold yellow")
            table.add_column("Name", style="cyan")
            table.add_column("Command", style="green")
            table.add_column("Status", style="magenta")
            table.add_column("Last Run", style="blue")
            
            for task in tasks:
                table.add_row(
                    str(task['id']),
                    task['name'],
                    task['command'][:50] + "..." if len(task['command']) > 50 else task['command'],
                    task['status'],
                    task['last_run'] or "Never"
                )
            
            console.print(table)
        else:
            console.print("[yellow]No automation tasks found[/yellow]")
    
    elif choice == "2":
        name = console.input("[bold cyan]Enter task name: [/bold cyan]")
        command = console.input("[bold cyan]Enter command to execute: [/bold cyan]")
        description = console.input("[bold cyan]Enter description (optional): [/bold cyan]")
        
        task = automation.create_task(name, command, description=description)
        console.print(f"[green]Task created with ID: {task['id']}[/green]")
    
    elif choice == "3":
        task_id = int(console.input("[bold cyan]Enter task ID to run: [/bold cyan]"))
        console.print("[yellow]Executing task...[/yellow]")
        
        result = automation.run_task(task_id)
        
        if result['status'] == "success":
            console.print(Panel.fit(
                f"Output:\n{result['output']}\n\nErrors:\n{result['error']}\n\nReturn Code: {result['return_code']}",
                title="Task Execution Result",
                border_style="green"
            ))
        else:
            console.print(f"[red]Error: {result['message']}[/red]")
    
    elif choice == "4":
        task_id = int(console.input("[bold cyan]Enter task ID to delete: [/bold cyan]"))
        automation.delete_task(task_id)
        console.print("[green]Task deleted successfully[/green]")
    
    elif choice == "5":
        name = console.input("[bold cyan]Enter task name: [/bold cyan]")
        command = console.input("[bold cyan]Enter command to execute: [/bold cyan]")
        schedule_type = console.input("[bold cyan]Enter schedule type (daily/hourly): [/bold cyan]")
        
        if schedule_type == "daily":
            schedule_value = console.input("[bold cyan]Enter time (HH:MM): [/bold cyan]")
        else:
            schedule_value = console.input("[bold cyan]Enter interval in hours: [/bold cyan]")
        
        result = automation.create_scheduled_task(name, command, schedule_type, schedule_value)
        
        if result['status'] == "success":
            console.print(f"[green]Scheduled task created successfully[/green]")
        else:
            console.print(f"[red]Error: {result['message']}[/red]")
    
    elif choice == "6":
        console.print("[yellow]Fetching scheduled tasks...[/yellow]")
        result = automation.list_scheduled_tasks()
        
        console.print(Panel.fit(
            result['output'] if result['status'] == "success" else result['message'],
            title="Scheduled Tasks",
            border_style="cyan"
        ))
    
    elif choice == "7":
        name = console.input("[bold cyan]Enter script name: [/bold cyan]")
        console.print("[yellow]Enter commands (one per line, type 'done' when finished):[/yellow]")
        
        commands = []
        while True:
            cmd = console.input()
            if cmd.lower() == 'done':
                break
            commands.append(cmd)
        
        result = automation.create_batch_script(name, commands)
        
        if result['status'] == "success":
            console.print(f"[green]{result['message']}[/green]")
        else:
            console.print(f"[red]Error: {result['message']}[/red]")
    
    elif choice == "8":
        script_path = console.input("[bold cyan]Enter script path: [/bold cyan]")
        console.print("[yellow]Executing script...[/yellow]")
        
        result = automation.execute_batch_script(script_path)
        
        if result['status'] == "success":
            console.print(Panel.fit(
                f"Output:\n{result['output']}\n\nErrors:\n{result['error']}",
                title="Script Execution Result",
                border_style="green"
            ))
        else:
            console.print(f"[red]Error: {result['message']}[/red]")
    
    console.input("\n[bold yellow]Press Enter to continue...[/bold yellow]")


if __name__ == "__main__":
    run()
