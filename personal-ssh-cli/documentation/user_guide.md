# Personal SSH/SCP CLI System Manager - User Guide

## Introduction

Welcome to the Personal SSH/SCP CLI System Manager! This comprehensive command-line tool helps you manage SSH connections and file transfers across your personal devices with professional-grade functionality and an intuitive interface.

## Installation

### Requirements

- Python 3.8 or higher
- pip (Python package manager)
- SSH client (OpenSSH recommended)

### Installation Steps

1. Install from the repository:
```bash
pip install -e .
```

2. Run the setup wizard:
```bash
pssh setup
```

## Getting Started

### Quick Start Guide

1. **Add your first device profile:**
```bash
pssh add-profile home-server --hostname 192.168.1.100 --username myuser
```

2. **Connect to the device:**
```bash
pssh connect home-server
```

3. **Execute commands:**
```bash
pssh exec conn_1 "ls -la"
```

4. **Transfer files:**
```bash
# Upload
pssh upload conn_1 /local/file.txt /remote/file.txt

# Download
pssh download conn_1 /remote/file.txt /local/file.txt
```

## Core Features

### Device Profile Management

Device profiles store connection information for quick access to your devices.

**Add a profile:**
```bash
pssh add-profile <name> --hostname <host> --username <user> [options]
```

**List profiles:**
```bash
pssh list-profiles
```

**Delete a profile:**
```bash
pssh delete-profile <name>
```

### Connection Management

**Connect to a device:**
```bash
pssh connect <profile-name>
```

**List active connections:**
```bash
pssh list-connections
```

**Disconnect all:**
```bash
pssh disconnect
```

### File Transfer

**Upload files:**
```bash
pssh upload <connection-id> <local-path> <remote-path>
```

**Download files:**
```bash
pssh download <connection-id> <remote-path> <local-path>
```

**Verify transfers:**
```bash
# Enabled by default, disable with --no-verify
pssh upload conn_1 file.txt /remote/ --no-verify
```

### Session Management

**List active sessions:**
```bash
pssh list-sessions
```

Sessions preserve your working directory and command history across connections.

## Configuration

Configuration files are stored in `~/.personal-ssh-cli/`:

- `config.yaml` - Main configuration
- `profiles.yaml` - Device profiles
- `sessions.json` - Session state
- `whitelist.json` - Approved devices
- `.secure.enc` - Encrypted credentials

### Settings

View and modify settings in `config.yaml`:

```yaml
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

## SSH Key Management

### Generate a new key:
```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519
```

### Use a key with a profile:
```bash
pssh add-profile server --hostname host.com --username user --key-file ~/.ssh/id_ed25519
```

## Best Practices

1. **Use SSH keys** instead of passwords for better security
2. **Enable host key verification** to prevent man-in-the-middle attacks
3. **Regular backups** of your configuration directory
4. **Use descriptive profile names** for easy identification
5. **Verify file transfers** for critical data

## Troubleshooting

### Connection Issues

**Problem:** Can't connect to device
- Check network connectivity: `ping <hostname>`
- Verify SSH service is running on remote device
- Check firewall settings

**Problem:** Authentication failed
- Verify username and key file path
- Check key file permissions (should be 600)
- Ensure public key is in remote `~/.ssh/authorized_keys`

### File Transfer Issues

**Problem:** Transfer failed
- Check available disk space on both systems
- Verify file paths and permissions
- Try with `--no-verify` to isolate checksum issues

### Performance Issues

**Problem:** Slow transfers
- Check network bandwidth
- Enable compression in settings
- Consider SSH multiplexing

## Advanced Usage

### Command Aliases

Create macros for frequently used commands (future feature).

### Scheduled Tasks

Automate regular maintenance operations (future feature).

### Device Discovery

Scan local network for SSH-enabled devices (future feature).

## Getting Help

**View command help:**
```bash
pssh <command> --help
```

**View version:**
```bash
pssh version
```

**Common commands:**
- `pssh connect` - Connect to a device
- `pssh upload` - Upload files
- `pssh download` - Download files
- `pssh list-connections` - View connections
- `pssh list-profiles` - View profiles

## Security Considerations

- Store SSH keys securely with appropriate permissions
- Use strong passphrases for SSH keys
- Enable host key verification
- Regularly review audit logs in `~/.personal-ssh-cli/logs/`
- Keep the system and dependencies updated

## Support

For issues or questions:
1. Check this user guide
2. Review troubleshooting section
3. Check the command reference documentation
4. Review audit logs for error details
