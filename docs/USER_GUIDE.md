# System Manager - Complete User Guide

## Overview

**System Manager** (Personal SSH CLI) is a comprehensive command-line interface for managing SSH connections and file transfers across your personal devices.

---

## 🎯 Two Setup Modes

### Mode 1: CLIENT Setup (Laptop/Device that connects TO others)
Run on the device you'll use to **initiate connections**:
```powershell
pssh setup
```

### Mode 2: SERVER Setup (Desktop/Device that accepts connections)
Run on the device you want to **connect TO** from other devices:
```powershell
pssh setup-server
```

---

## 📋 Complete Workflow Example

### Scenario: Connect from Laptop to Desktop

#### Step 1: On Your DESKTOP (Server)

```powershell
# Navigate to the project directory
cd D:\AMD\projects\System-Manager

# Test IP detection first (optional but recommended)
pssh test-ip

# Run server setup
pssh setup-server
```

**During setup you'll be asked:**
- Which IP address to use (select from detected or enter custom)
- Enable SSH server? (y/n)
- Generate SSH keys? (y/n)
- Profile name (default: your hostname)

**Output:**
```
Configuration saved to: C:\Users\AMD\.personal-ssh-cli\DESKTOP-PC_profile.json
```

#### Step 2: Transfer Configuration File

Copy the generated JSON file to your laptop:
- Via USB drive
- Email attachment
- Network share
- Cloud storage (OneDrive, Dropbox, etc.)

#### Step 3: On Your LAPTOP (Client)

```powershell
# First-time setup on laptop
pssh setup

# Import the desktop profile
pssh import-profile DESKTOP-PC_profile.json

# Or specify custom name
pssh import-profile DESKTOP-PC_profile.json --name my-desktop

# Verify the profile was added
pssh list-profiles

# Connect to your desktop
pssh connect my-desktop
```

---

## 🎮 Available Commands

### Setup & Configuration

| Command | Description | Run On |
|---------|-------------|--------|
| `pssh setup` | Configure as SSH client | Laptop/Client |
| `pssh setup-server` | Configure as SSH server | Desktop/Server |
| `pssh test-ip` | Test IP detection | Any device |

### Profile Management

| Command | Description |
|---------|-------------|
| `pssh add-profile <name>` | Manually add a device profile |
| `pssh import-profile <file>` | Import profile from JSON file |
| `pssh list-profiles` | Show all configured profiles |
| `pssh delete-profile <name>` | Remove a profile |

### Connection Management

| Command | Description |
|---------|-------------|
| `pssh connect <profile>` | Connect to a device |
| `pssh disconnect` | Disconnect all connections |
| `pssh list-connections` | Show active connections |
| `pssh list-sessions` | Show active sessions |

### File Transfer

| Command | Description |
|---------|-------------|
| `pssh upload <local> <profile>:<remote>` | Upload file to remote |
| `pssh download <profile>:<remote> <local>` | Download file from remote |

### Remote Execution

| Command | Description |
|---------|-------------|
| `pssh exec <profile> "<command>"` | Execute command on remote |

### Information

| Command | Description |
|---------|-------------|
| `pssh --help` | Show all commands |
| `pssh version` | Show version info |

---

## 💡 Common Usage Patterns

### 1. Quick Server Setup with Defaults

```powershell
# On desktop - auto-accept defaults
pssh setup-server --auto-yes
```

### 2. Manual Profile Creation (Alternative)

```powershell
# If you don't want to use JSON import
pssh add-profile my-desktop
# Follow the prompts to enter:
# - Hostname: 192.168.0.14
# - Username: AMD
# - Port: 22
# - Key file: (optional)
```

### 3. Upload Files

```powershell
# Upload single file
pssh upload C:\Users\AMD\Documents\file.txt my-desktop:~/Desktop/

# Upload directory (if supported)
pssh upload C:\Projects\MyApp my-desktop:~/Projects/
```

### 4. Download Files

```powershell
# Download single file
pssh download my-desktop:~/Documents/report.pdf C:\Downloads\

# Download to current directory
pssh download my-desktop:~/backup.zip .
```

### 5. Execute Remote Commands

```powershell
# Check disk space on desktop
pssh exec my-desktop "df -h"

# Windows commands
pssh exec my-desktop "dir C:\Users"

# Get system info
pssh exec my-desktop "systeminfo"
```

### 6. Multiple Device Setup

```powershell
# Set up multiple servers
# On Desktop 1:
pssh setup-server  # Creates desktop1_profile.json

# On Desktop 2:
pssh setup-server  # Creates desktop2_profile.json

# On Raspberry Pi:
pssh setup-server  # Creates raspberrypi_profile.json

# On Laptop (import all):
pssh import-profile desktop1_profile.json --name desktop1
pssh import-profile desktop2_profile.json --name desktop2
pssh import-profile raspberrypi_profile.json --name pi

# List all profiles
pssh list-profiles

# Connect to any
pssh connect desktop1
pssh connect pi
```

---

## 🔧 Configuration Files

### Location
```
C:\Users\<Username>\.personal-ssh-cli\
├── config.yaml           # Global settings
├── profiles.yaml         # Device profiles
└── <hostname>_profile.json  # Generated server configs
```

### config.yaml Structure

```yaml
version: 1.0.0
settings:
  auto_reconnect: true
  auto_save_sessions: true
  color_output: true
  confirmation_prompts: true
  connection_timeout: 30
  default_profile: null
  session_history_size: 1000
  transfer_timeout: 300
security:
  key_type: ed25519
  session_lock_timeout: 1800
  verify_host_keys: true
performance:
  bandwidth_limit: 0
  compression: true
  ssh_multiplexing: true
ui:
  notifications: true
  progress_bars: true
  terminal_width: auto
```

### profiles.yaml Structure

```yaml
profiles:
  my-desktop:
    host: 192.168.0.14
    username: AMD
    port: 22
    auth_method: key
    key_file: C:\Users\AMD\.ssh\id_ed25519
    description: "Windows Desktop - DESKTOP-PC"
    verify_host_keys: true
    compression: true
    
  raspberry-pi:
    host: 192.168.0.50
    username: pi
    port: 22
    auth_method: password
    description: "Raspberry Pi 4"
    
tags:
  home: [my-desktop, raspberry-pi]
  servers: [my-desktop]
  work: []
```

---

## 🔐 SSH Authentication

### Password Authentication
- Simple but less secure
- Will prompt for password on each connection
- No additional setup needed

### Key-Based Authentication (Recommended)

**Generate keys during server setup:**
```powershell
# When prompted during 'pssh setup-server'
Generate SSH keys? (y/n): y
```

**Or generate manually:**
```powershell
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519
```

**Copy public key to server:**
```powershell
# From laptop, copy public key
cat ~/.ssh/id_ed25519.pub

# On desktop, add to authorized_keys
# Windows:
echo "your-public-key-here" >> C:\Users\AMD\.ssh\authorized_keys

# Linux:
echo "your-public-key-here" >> ~/.ssh/authorized_keys
```

---

## 🌐 Network Scenarios

### Same Network (Home/Office WiFi)
- Use local IP (e.g., `192.168.0.14`)
- Fast and secure
- No internet required

### Different Networks (Remote Access)

**Option 1: VPN**
- Most secure
- Access devices using local IPs through VPN tunnel

**Option 2: Port Forwarding**
- Configure router to forward port 22
- Use public IP address
- Security risk - use strong authentication

**Option 3: SSH Tunneling**
- Use intermediate jump server
- Configure with ProxyJump

---

## 🐛 Troubleshooting

### "Connection refused"

**Check SSH server is running:**
```powershell
# Windows
Get-Service sshd

# Start if not running
Start-Service sshd
```

**Check firewall:**
```powershell
# Verify SSH port 22 is allowed
Get-NetFirewallRule -DisplayName "*ssh*"
```

### "Permission denied"

**Verify credentials:**
- Check username is correct
- For key auth, ensure public key is in `authorized_keys`
- For password auth, verify password is correct

### "Host key verification failed"

**Remove old host key:**
```powershell
ssh-keygen -R 192.168.0.14
```

### Wrong IP Address Detected

**Use test-ip to verify:**
```powershell
pssh test-ip
```

**During setup, select correct IP or enter manually:**
```
Which IP should be used for SSH connections? [1-2] or enter custom: 192.168.0.14
```

### Import Errors

**Verify JSON file format:**
```json
{
  "profile_name": "my-desktop",
  "host": "192.168.0.14",
  "username": "AMD",
  "port": 22,
  "auth_method": "key",
  "key_file": "~/.ssh/id_ed25519",
  "description": "Windows - DESKTOP-PC"
}
```

---

## 📊 Advanced Features

### Session Management
```powershell
# List all active sessions
pssh list-sessions

# Sessions persist across connections
# View session history and command logs
```

### Connection Multiplexing
- Reuses SSH connections for better performance
- Configured in `config.yaml`:
  ```yaml
  performance:
    ssh_multiplexing: true
  ```

### Auto-Reconnection
- Automatically reconnects on connection drop
- Configure in `config.yaml`:
  ```yaml
  settings:
    auto_reconnect: true
  ```

### Custom Configuration Directory
```powershell
# Use custom config location
pssh --config-dir D:\MyConfigs list-profiles
```

---

## 🔄 Quick Reference

### Initial Setup Workflow
```powershell
# On DESKTOP (Server):
cd D:\AMD\projects\System-Manager
pssh test-ip                    # Verify IP
pssh setup-server               # Configure server
# Transfer generated JSON file to laptop

# On LAPTOP (Client):
pssh setup                      # Configure client
pssh import-profile desktop_profile.json
pssh connect my-desktop         # Connect!
```

### Daily Usage
```powershell
# Connect
pssh connect my-desktop

# Upload file
pssh upload file.txt my-desktop:~/

# Download file
pssh download my-desktop:~/file.txt .

# Execute command
pssh exec my-desktop "dir"

# Disconnect
pssh disconnect
```

---

## 📚 Additional Resources

- **Command Reference:** `personal-ssh-cli/documentation/command_reference.md`
- **Troubleshooting:** `personal-ssh-cli/documentation/troubleshooting.md`
- **User Guide:** `personal-ssh-cli/documentation/user_guide.md`
- **Automated Setup:** `AUTOMATED_SETUP_GUIDE.md`

---

## 🆘 Getting Help

```powershell
# General help
pssh --help

# Command-specific help
pssh connect --help
pssh upload --help
pssh setup-server --help

# Check version
pssh version

# Test configuration
pssh test-ip
pssh list-profiles
```

---

## ✨ Tips & Best Practices

1. **Always test IP detection first:** `pssh test-ip`
2. **Use key-based authentication** for security
3. **Keep profiles organized** with descriptive names
4. **Backup your config directory** regularly
5. **Use tags** in `profiles.yaml` to organize devices
6. **Enable auto-reconnect** for unstable connections
7. **Set a default_profile** for quick connections
8. **Use confirmation_prompts** to prevent mistakes

---

**Version:** 1.0.0  
**Last Updated:** December 18, 2025
