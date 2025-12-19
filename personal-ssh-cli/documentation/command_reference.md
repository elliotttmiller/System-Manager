# Command Reference

Complete reference for all Personal SSH/SCP CLI commands.

## Global Options

```bash
--config-dir PATH    Use custom configuration directory
--help              Show help message
```

## Commands

### setup

Run interactive setup wizard.

**Usage:**
```bash
pssh setup
```

**Description:**
Initializes the system, creates configuration directory, and checks for SSH keys.

---

### connect

Connect to a device using a saved profile.

**Usage:**
```bash
pssh connect <profile-name>
```

**Arguments:**
- `profile-name` - Name of the device profile

**Examples:**
```bash
pssh connect home-server
pssh connect work-laptop
```

---

### disconnect

Disconnect all active connections.

**Usage:**
```bash
pssh disconnect
```

---

### exec

Execute a command on a remote connection.

**Usage:**
```bash
pssh exec <connection-id> <command>
```

**Arguments:**
- `connection-id` - Connection identifier
- `command` - Command to execute (quote if contains spaces)

**Examples:**
```bash
pssh exec conn_1 "ls -la"
pssh exec conn_1 "df -h"
pssh exec conn_1 "ps aux | grep python"
```

---

### upload

Upload a file to a remote system.

**Usage:**
```bash
pssh upload <connection-id> <local-path> <remote-path> [options]
```

**Arguments:**
- `connection-id` - Connection identifier
- `local-path` - Local file path
- `remote-path` - Remote destination path

**Options:**
- `--verify` - Verify file integrity (default)
- `--no-verify` - Skip verification

**Examples:**
```bash
pssh upload conn_1 /local/file.txt /remote/file.txt
pssh upload conn_1 ./document.pdf ~/documents/
pssh upload conn_1 backup.tar.gz /tmp/ --no-verify
```

---

### download

Download a file from a remote system.

**Usage:**
```bash
pssh download <connection-id> <remote-path> <local-path> [options]
```

**Arguments:**
- `connection-id` - Connection identifier
- `remote-path` - Remote file path
- `local-path` - Local destination path

**Options:**
- `--verify` - Verify file integrity (default)
- `--no-verify` - Skip verification

**Examples:**
```bash
pssh download conn_1 /remote/file.txt /local/file.txt
pssh download conn_1 ~/logs/app.log ./logs/
pssh download conn_1 /var/log/syslog ./syslog --no-verify
```

---

### list-connections

List all active connections.

**Usage:**
```bash
pssh list-connections
```

**Output:**
Displays a table with:
- Connection ID
- Hostname
- Username
- Connection status

---

### list-profiles

List all saved device profiles.

**Usage:**
```bash
pssh list-profiles
```

---

### add-profile

Add a new device profile.

**Usage:**
```bash
pssh add-profile <name> [options]
```

**Arguments:**
- `name` - Profile name (unique)

**Options:**
- `--hostname TEXT` - Hostname or IP address (required)
- `--username TEXT` - SSH username (required)
- `--port INTEGER` - SSH port (default: 22)
- `--key-file PATH` - Path to SSH key file

**Examples:**
```bash
pssh add-profile home-server --hostname 192.168.1.100 --username user
pssh add-profile work --hostname work.example.com --username admin --key-file ~/.ssh/work_key
pssh add-profile custom --hostname 10.0.0.50 --username root --port 2222
```

---

### delete-profile

Delete a device profile.

**Usage:**
```bash
pssh delete-profile <name>
```

**Arguments:**
- `name` - Profile name to delete

**Examples:**
```bash
pssh delete-profile old-server
```

---

### list-sessions

List all active sessions.

**Usage:**
```bash
pssh list-sessions
```

**Output:**
Displays a table with:
- Session ID
- Profile name
- State (active/background/suspended)
- Created timestamp
- Command count

---

### version

Display version information.

**Usage:**
```bash
pssh version
```

---

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Connection error
- `3` - File not found
- `4` - Authentication error
- `130` - Interrupted by user (Ctrl+C)

## Configuration Files

### config.yaml

Main configuration file located at `~/.personal-ssh-cli/config.yaml`.

**Structure:**
```yaml
version: '1.0.0'
settings:
  default_profile: null
  auto_reconnect: true
  connection_timeout: 30
  color_output: true
security:
  verify_host_keys: true
  key_type: 'ed25519'
performance:
  compression: true
  ssh_multiplexing: true
```

### profiles.yaml

Device profiles located at `~/.personal-ssh-cli/profiles.yaml`.

**Structure:**
```yaml
profiles:
  home-server:
    hostname: 192.168.1.100
    username: user
    port: 22
    key_file: /home/user/.ssh/id_ed25519
    verify_host_keys: true
    compression: true
tags:
  work: [work-laptop, work-server]
  home: [home-server, raspberry-pi]
```

## Environment Variables

- `PSSH_CONFIG_DIR` - Override default configuration directory
- `SSH_AUTH_SOCK` - SSH agent socket (standard SSH variable)

## Tips and Tricks

1. **Use tab completion** (future feature) for profile names and connection IDs
2. **Create profile aliases** for frequently used devices
3. **Enable SSH multiplexing** for faster subsequent connections
4. **Use compression** on slow connections
5. **Verify critical transfers** but skip verification for large non-critical files

## Related Commands

Standard SSH/SCP commands that work alongside this tool:

```bash
ssh user@host                    # Standard SSH connection
scp file.txt user@host:/path/    # Standard SCP transfer
ssh-keygen -t ed25519           # Generate SSH key
ssh-copy-id user@host           # Copy public key to remote
```
