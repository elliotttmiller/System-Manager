"""
Seamless Script Execution Feature

Uploads a local script to a remote device and executes it, returning output.

This feature uses the project's ConnectionManager and FileTransfer APIs.
"""
from pathlib import Path
from typing import Optional

from core.file_transfer import FileTransfer


class SeamlessScriptExecutor:
    """Upload and execute a local script on a remote device."""

    def __init__(self, connection_manager, ui=None):
        self.connection_manager = connection_manager
        self.ui = ui

    def run(self, target: str, local_script: str, remote_path: Optional[str] = None,
            interpreter: Optional[str] = None, keep_file: bool = False, timeout: int = 0) -> dict:
        """Run a local script on a remote target.

        Args:
            target: Either an existing connection_id (e.g., conn_1) or a profile name
            local_script: Path to the local script to upload
            remote_path: Optional destination path on remote (defaults to /tmp/<name>)
            interpreter: Optional interpreter to run the script (e.g. /bin/bash, /usr/bin/python3)
            keep_file: If True, do not remove the remote script after execution
            timeout: Command timeout in seconds (0 = no timeout)

        Returns:
            A dict with keys: success (bool), stdout, stderr, exit_code, error (if any)
        """
        # Determine if target is a connection id or profile name
        conn = None
        conn_obj = self.connection_manager.get_connection(target)
        created_conn = False

        try:
            if conn_obj:
                conn_id = target
            else:
                # Treat as profile name and create connection
                conn_id = self.connection_manager.create_connection(target)
                created_conn = True

            # Establish connection (returns SSHConnection)
            ssh_conn = self.connection_manager.connect(conn_id)
            if not ssh_conn:
                return {'success': False, 'error': 'Failed to establish SSH connection'}

            # Prepare remote path
            local_path = Path(local_script)
            if not local_path.exists():
                return {'success': False, 'error': f'Local script not found: {local_script}'}

            if not remote_path:
                remote_path = f"/tmp/{local_path.name}"

            # Upload
            ft = FileTransfer(ssh_conn)
            if self.ui:
                self.ui.print(f"Uploading {local_script} -> {remote_path}...")

            upload_res = ft.upload_file(str(local_path), remote_path, verify=True)
            if not upload_res.get('success'):
                return {'success': False, 'error': f"Upload failed: {upload_res.get('error')}"}

            # Make executable
            try:
                ssh_conn.execute_command(f"chmod +x '{remote_path}'")
            except Exception:
                # Not fatal; continue
                pass

            # Build execution command
            if interpreter:
                cmd = f"{interpreter} '{remote_path}'"
            else:
                cmd = f"'{remote_path}'"

            if self.ui:
                self.ui.print_info(f"Executing script on remote: {cmd}")

            exec_res = ssh_conn.execute_command(cmd, timeout=timeout if timeout > 0 else None)

            # Optionally remove remote file
            if not keep_file:
                try:
                    ssh_conn.execute_command(f"rm -f '{remote_path}'")
                except Exception:
                    pass

            return {
                'success': True,
                'stdout': exec_res.get('stdout', ''),
                'stderr': exec_res.get('stderr', ''),
                'exit_code': exec_res.get('exit_code', 0),
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            # If we created a connection for this run, disconnect it
            try:
                if created_conn:
                    self.connection_manager.disconnect(conn_id)
            except Exception:
                pass
