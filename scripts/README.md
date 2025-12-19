# Scripts Directory

This directory contains utility scripts for the System Manager.

## Available Scripts

### setup_ssh_server.py
**Purpose:** Configure a device as an SSH server that can accept connections from other devices.

**Usage:**
```powershell
python scripts/setup_ssh_server.py
```

**When to use:**
- Run on your DESKTOP/SERVER (the device you want to connect TO)
- Automatically detects system information
- Enables SSH server if needed
- Generates configuration profile for import on client devices

**Output:**
- Creates `~/.personal-ssh-cli/<hostname>_profile.json`
- Transfer this file to your laptop/client device

---

### test_ip_detection.py
**Purpose:** Test and display all detected IP addresses on the current device.

**Usage:**
```powershell
python scripts/test_ip_detection.py
```

**When to use:**
- Before running setup to verify which IP will be used
- To troubleshoot IP detection issues
- To see all available network interfaces

**Output:**
- Lists all detected IPv4 addresses
- Indicates which will be used as primary

---

## Quick Start Examples

### Setup Desktop as SSH Server
```powershell
# Navigate to project root
cd D:\AMD\projects\System-Manager

# Test IP detection first (optional)
python scripts/test_ip_detection.py

# Run server setup
python scripts/setup_ssh_server.py
```

### Alternative: Use CLI Commands
```powershell
# These scripts are also available as CLI commands
pssh test-ip
pssh setup-server
```

The CLI commands (`pssh`) are the recommended way to use these features.

---

## Notes

- These scripts are standalone utilities
- They can be run independently of the main CLI
- For regular use, prefer the `pssh` CLI commands
- Scripts are useful for automation or scripting scenarios
