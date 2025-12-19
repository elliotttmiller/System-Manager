# Personal SSH/SCP CLI System Manager

A comprehensive, Python-based command-line interface system manager exclusively for personal SSH/SCP operations across your owned devices.

## 🎯 Overview

This tool provides professional-grade SSH connection management and file transfer capabilities through an intuitive CLI experience, designed specifically for single-user personal infrastructure management.

## ✨ Key Features

- **Device Profile Management** - Save and manage SSH connection profiles for all your devices
- **Seamless Connections** - Quick SSH connections with automatic authentication
- **Smart File Transfers** - SCP/SFTP transfers with integrity verification and resume capability
- **Session Management** - Persistent sessions that survive application restarts
- **Security First** - SSH key-based authentication, host key verification, and encrypted credential storage
- **Rich Terminal UI** - Color-coded output, progress bars, and interactive menus
- **Cross-Platform** - Works on Windows, Linux, and macOS
- **Offline-First** - Full functionality without internet connectivity

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/elliotttmiller/System-Manager.git
cd System-Manager

# Install the package
pip install -e .

# Run setup wizard
pssh setup
```

### Basic Usage

```bash
# Add a device profile
pssh add-profile home-server --hostname 192.168.1.100 --username myuser

# Connect to the device
pssh connect home-server

# Execute a command
pssh exec conn_1 "ls -la"

# Transfer files
pssh upload conn_1 /local/file.txt /remote/file.txt
pssh download conn_1 /remote/log.txt /local/log.txt

# List connections and sessions
pssh list-connections
pssh list-sessions
```

## 📚 Documentation

- **[User Guide](personal-ssh-cli/documentation/user_guide.md)** - Complete usage instructions
- **[Command Reference](personal-ssh-cli/documentation/command_reference.md)** - Full command listing with examples
- **[Troubleshooting](personal-ssh-cli/documentation/troubleshooting.md)** - Common issue resolution

## 🏗️ Architecture

```
personal-ssh-cli/
├── core/              # Core system components
│   ├── cli_engine.py           # Main CLI entry point
│   ├── connection_manager.py   # SSH connection management
│   ├── file_transfer.py        # File transfer operations
│   ├── config_manager.py       # Configuration management
│   └── session_manager.py      # Session tracking
├── security/          # Security components
│   ├── auth_manager.py         # Authentication management
│   ├── device_whitelist.py     # Device approval system
│   └── audit_logger.py         # Activity logging
├── features/          # Advanced features
│   ├── automation.py           # Command sequences
│   ├── device_discovery.py     # Network scanning
│   ├── monitoring.py           # Performance monitoring
│   └── utils.py                # Utility functions
├── interface/         # User interface
│   ├── terminal_ui.py          # Rich terminal UI
│   ├── help_system.py          # Context-aware help
│   ├── autocomplete.py         # Tab completion
│   └── notifications.py        # System notifications
└── adapters/          # Platform adapters
    ├── windows.py              # Windows integration
    ├── linux_remote.py         # Linux remote support
    └── macos_remote.py         # macOS remote support
```

## 🔧 Requirements

- Python 3.8 or higher
- SSH client (OpenSSH recommended)
- pip (Python package manager)

### Python Dependencies

- paramiko - SSH protocol implementation
- scp - SCP file transfer
- rich - Terminal UI
- click - CLI framework
- pyyaml - Configuration management
- cryptography - Secure credential storage
- psutil - System monitoring
- tqdm - Progress tracking

## 🎨 Features in Detail

### Connection Management
- Profile-based connection management
- Automatic reconnection with state preservation
- Connection health monitoring
- SSH multiplexing support
- Session persistence across restarts

### File Transfer
- Multi-protocol support (SCP/SFTP)
- Resume capability for interrupted transfers
- SHA-256 integrity verification
- Directory synchronization
- Real-time transfer statistics

### Security
- SSH key-based authentication
- Host key verification
- Device whitelist management
- AES-256 encrypted credential storage
- Local audit logging

### User Interface
- Color-coded terminal output
- Progress bars for file transfers
- Interactive menus
- Context-aware help system
- Tab completion (planned)

## 💻 Platform Support

- **Windows** - Full support with PowerShell integration
- **Linux** - Native support for all major distributions
- **macOS** - Full support with Homebrew integration
- **Remote Devices** - Linux and macOS remote device management

## 🔒 Security

- All credentials encrypted using AES-256
- SSH keys stored with proper permissions
- Host key verification prevents MITM attacks
- Local audit logging for all activities
- No cloud dependencies or external API calls

## 📊 Performance

- Startup time: < 3 seconds
- Memory usage: < 150MB under normal operation
- File transfer: 85%+ bandwidth utilization
- Connection establishment: < 3 seconds on local networks

## 🛠️ Configuration

Configuration is stored in `~/.personal-ssh-cli/`:

```yaml
# config.yaml
settings:
  auto_reconnect: true
  connection_timeout: 30
  color_output: true

security:
  verify_host_keys: true
  key_type: ed25519

performance:
  compression: true
  ssh_multiplexing: true
```

## 📝 Examples

### Managing Multiple Devices

```bash
# Add multiple profiles
pssh add-profile home-server --hostname 192.168.1.100 --username admin
pssh add-profile work-laptop --hostname work.example.com --username user
pssh add-profile raspberry-pi --hostname 192.168.1.50 --username pi

# Connect to devices
pssh connect home-server
pssh connect raspberry-pi

# View all connections
pssh list-connections
```

### File Operations

```bash
# Upload with verification
pssh upload conn_1 /local/backup.tar.gz /remote/backups/

# Download without verification (faster)
pssh download conn_1 /remote/large-file.iso /local/ --no-verify

# Verify remote directory contents
pssh exec conn_1 "ls -lh /remote/backups/"
```

### Automation (Planned)

```bash
# Create command macro
pssh create-macro backup-routine \
  "tar -czf backup.tar.gz /important/data" \
  "mv backup.tar.gz /backups/$(date +%Y%m%d).tar.gz"

# Execute macro
pssh run-macro backup-routine conn_1
```

## 🤝 Contributing

This is a personal use tool. Feel free to fork and customize for your own needs.

## 📜 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built with:
- [Paramiko](https://www.paramiko.org/) - SSH protocol
- [Rich](https://rich.readthedocs.io/) - Terminal UI
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Cryptography](https://cryptography.io/) - Security

## 📮 Contact

For issues or questions, please open an issue on GitHub.

---

**Note:** This tool is designed for personal use managing your own devices. Always follow security best practices and keep your SSH keys secure.