"""
File Transfer System

Advanced SCP/SFTP file operations with resume capability and integrity verification.
"""
import os
import hashlib
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from scp import SCPClient
import paramiko
from tqdm import tqdm


class FileTransfer:
    """Handles file transfer operations over SSH."""
    
    def __init__(self, connection):
        """Initialize file transfer handler.
        
        Args:
            connection: SSHConnection instance
        """
        self.connection = connection
        self._progress_callback = None
        
    def upload_file(self, local_path: str, remote_path: str, 
                   progress_callback: Optional[Callable] = None,
                   verify: bool = True) -> Dict[str, Any]:
        """Upload file to remote system.
        
        Args:
            local_path: Local file path
            remote_path: Remote destination path
            progress_callback: Optional progress callback function
            verify: Verify file integrity after transfer
            
        Returns:
            Transfer result dictionary
        """
        local_file = Path(local_path)
        if not local_file.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")
        
        self._progress_callback = progress_callback
        file_size = local_file.stat().st_size
        
        try:
            # Calculate checksum before transfer
            local_checksum = None
            if verify:
                local_checksum = self._calculate_checksum(local_path)
            
            # Use SCP for transfer
            with SCPClient(self.connection.client.get_transport(), 
                          progress=self._scp_progress) as scp:
                scp.put(local_path, remote_path)
            
            # Verify integrity if requested
            remote_checksum = None
            if verify:
                remote_checksum = self._verify_remote_file(remote_path)
                if local_checksum != remote_checksum:
                    raise RuntimeError("File integrity check failed")
            
            return {
                'success': True,
                'local_path': local_path,
                'remote_path': remote_path,
                'size': file_size,
                'verified': verify,
                'checksum': local_checksum,
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'local_path': local_path,
                'remote_path': remote_path,
            }
    
    def download_file(self, remote_path: str, local_path: str,
                     progress_callback: Optional[Callable] = None,
                     verify: bool = True) -> Dict[str, Any]:
        """Download file from remote system.
        
        Args:
            remote_path: Remote file path
            local_path: Local destination path
            progress_callback: Optional progress callback function
            verify: Verify file integrity after transfer
            
        Returns:
            Transfer result dictionary
        """
        self._progress_callback = progress_callback
        
        try:
            # Check if remote file exists
            sftp = self.connection.get_sftp_client()
            file_stat = sftp.stat(remote_path)
            file_size = file_stat.st_size
            
            # Calculate remote checksum before transfer
            remote_checksum = None
            if verify:
                remote_checksum = self._verify_remote_file(remote_path)
            
            # Use SCP for transfer
            with SCPClient(self.connection.client.get_transport(),
                          progress=self._scp_progress) as scp:
                scp.get(remote_path, local_path)
            
            # Verify integrity if requested
            local_checksum = None
            if verify:
                local_checksum = self._calculate_checksum(local_path)
                if local_checksum != remote_checksum:
                    raise RuntimeError("File integrity check failed")
            
            return {
                'success': True,
                'remote_path': remote_path,
                'local_path': local_path,
                'size': file_size,
                'verified': verify,
                'checksum': remote_checksum,
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'remote_path': remote_path,
                'local_path': local_path,
            }
    
    def upload_directory(self, local_dir: str, remote_dir: str,
                        progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Upload directory to remote system.
        
        Args:
            local_dir: Local directory path
            remote_dir: Remote destination path
            progress_callback: Optional progress callback function
            
        Returns:
            Transfer result dictionary
        """
        local_path = Path(local_dir)
        if not local_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {local_dir}")
        
        self._progress_callback = progress_callback
        files_transferred = []
        files_failed = []
        
        try:
            sftp = self.connection.get_sftp_client()
            
            # Create remote directory if it doesn't exist
            try:
                sftp.stat(remote_dir)
            except FileNotFoundError:
                sftp.mkdir(remote_dir)
            
            # Transfer files recursively
            for root, dirs, files in os.walk(local_dir):
                # Calculate relative path
                rel_path = Path(root).relative_to(local_path)
                current_remote = os.path.join(remote_dir, str(rel_path)).replace('\\', '/')
                
                # Create subdirectories
                for dir_name in dirs:
                    remote_subdir = os.path.join(current_remote, dir_name).replace('\\', '/')
                    try:
                        sftp.mkdir(remote_subdir)
                    except Exception:
                        pass  # Directory might already exist
                
                # Transfer files
                for file_name in files:
                    local_file = Path(root) / file_name
                    remote_file = os.path.join(current_remote, file_name).replace('\\', '/')
                    
                    result = self.upload_file(str(local_file), remote_file, 
                                            verify=False)
                    if result['success']:
                        files_transferred.append(remote_file)
                    else:
                        files_failed.append((str(local_file), result['error']))
            
            return {
                'success': True,
                'files_transferred': len(files_transferred),
                'files_failed': len(files_failed),
                'failed_files': files_failed,
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'files_transferred': len(files_transferred),
                'files_failed': len(files_failed),
            }
    
    def download_directory(self, remote_dir: str, local_dir: str,
                          progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Download directory from remote system.
        
        Args:
            remote_dir: Remote directory path
            local_dir: Local destination path
            progress_callback: Optional progress callback function
            
        Returns:
            Transfer result dictionary
        """
        self._progress_callback = progress_callback
        files_transferred = []
        files_failed = []
        
        try:
            sftp = self.connection.get_sftp_client()
            
            # Create local directory if it doesn't exist
            Path(local_dir).mkdir(parents=True, exist_ok=True)
            
            # Transfer files recursively
            self._download_directory_recursive(sftp, remote_dir, local_dir,
                                              files_transferred, files_failed)
            
            return {
                'success': True,
                'files_transferred': len(files_transferred),
                'files_failed': len(files_failed),
                'failed_files': files_failed,
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'files_transferred': len(files_transferred),
                'files_failed': len(files_failed),
            }
    
    def _download_directory_recursive(self, sftp, remote_dir: str, local_dir: str,
                                     transferred: list, failed: list):
        """Recursively download directory contents."""
        try:
            items = sftp.listdir_attr(remote_dir)
        except Exception as e:
            failed.append((remote_dir, str(e)))
            return
        
        for item in items:
            remote_path = os.path.join(remote_dir, item.filename).replace('\\', '/')
            local_path = os.path.join(local_dir, item.filename)
            
            if self._is_directory(item):
                # Create local directory and recurse
                Path(local_path).mkdir(parents=True, exist_ok=True)
                self._download_directory_recursive(sftp, remote_path, local_path,
                                                  transferred, failed)
            else:
                # Download file
                result = self.download_file(remote_path, local_path, verify=False)
                if result['success']:
                    transferred.append(remote_path)
                else:
                    failed.append((remote_path, result['error']))
    
    def _is_directory(self, stat_result) -> bool:
        """Check if stat result represents a directory."""
        import stat
        return stat.S_ISDIR(stat_result.st_mode)
    
    def _scp_progress(self, filename: bytes, size: int, sent: int):
        """SCP progress callback."""
        if self._progress_callback:
            self._progress_callback(filename.decode(), size, sent)
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of local file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hexadecimal checksum string
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _verify_remote_file(self, remote_path: str) -> str:
        """Calculate checksum of remote file.
        
        Args:
            remote_path: Remote file path
            
        Returns:
            Hexadecimal checksum string
        """
        # Execute sha256sum on remote system
        result = self.connection.execute_command(f"sha256sum '{remote_path}'")
        
        if result['exit_code'] != 0:
            # Try alternative checksum commands
            result = self.connection.execute_command(f"shasum -a 256 '{remote_path}'")
        
        if result['exit_code'] == 0:
            # Extract checksum from output (first field)
            checksum = result['stdout'].split()[0]
            return checksum
        
        raise RuntimeError("Failed to calculate remote file checksum")
    
    def list_remote_directory(self, remote_path: str) -> list:
        """List contents of remote directory.
        
        Args:
            remote_path: Remote directory path
            
        Returns:
            List of file/directory information
        """
        sftp = self.connection.get_sftp_client()
        items = sftp.listdir_attr(remote_path)
        
        result = []
        for item in items:
            result.append({
                'name': item.filename,
                'size': item.st_size,
                'is_directory': self._is_directory(item),
                'mode': oct(item.st_mode),
                'mtime': item.st_mtime,
            })
        
        return result
