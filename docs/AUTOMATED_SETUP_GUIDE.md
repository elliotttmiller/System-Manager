# Automated SSH Server Setup Guide

## Overview

This guide explains how to use the automated setup system to configure your **desktop** as an SSH server that your **laptop** can connect to.

---

## 🎯 Quick Start

### Step 1: On Your Desktop (Server)

Run the automated setup script:

```bash
# Navigate to the project directory
cd D:\AMD\projects\System-Manager

# Run the setup script
python setup_ssh_server.py
```

**The script will:**
- ✅ Detect your system information (IP, hostname, OS)
- ✅ Check if SSH server is installed/running
- ✅ Offer to enable SSH server (if not running)
- ✅ Optionally generate SSH keys
- ✅ Create a profile configuration file

### Step 2: Transfer Configuration

After setup completes, you'll find a JSON file at:
```
C:\Users\AMD\.personal-ssh-cli\<hostname>_profile.json
```

**Transfer this file to your laptop** using:
- USB drive
- Email
- Cloud storage (Dropbox, OneDrive, etc.)
- Network share

### Step 3: On Your Laptop (Client)

Import the profile:

```powershell
# Import the profile configuration
pssh import-profile desktop_profile.json

# Connect to your desktop
pssh connect <profile-name>
```

---

## 📋 Detailed Steps

### Desktop Setup (Automated)

#### Option A: Using the Setup Script

```powershell
# Run the interactive setup
python setup_ssh_server.py
```

**You'll be prompted for:**

1. **Enable SSH Server?** (y/n)
   - Say `y` if SSH is not running
   - Requires Administrator privileges on Windows

2. **Generate SSH Keys?** (y/n)
   - Recommended for key-based authentication
   - Creates `~/.ssh/id_ed25519` key pair

3. **Profile Name**
   - Default: Your computer's hostname
   - Or enter a custom name

**Output:**
```
✅ Configuration saved to: C:\Users\AMD\.personal-ssh-cli\my-desktop_profile.json

📋 SETUP SUMMARY
================
🖥️  Device Information:
   Hostname: DESKTOP-PC
   OS: Windows 10.0.19045
   Username: AMD

🌐 Network Information:
   IP 1: 192.168.1.100
   IP 2: 127.0.0.1
   SSH Port: 22

📝 Profile Configuration:
   Profile Name: my-desktop
   Connection: ssh AMD@192.168.1.100
```

#### Option B: Manual Setup

If you prefer manual configuration:

1. **Enable SSH Server on Windows:**
   ```powershell
   # Run as Administrator
   Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
   Start-Service sshd
   Set-Service -Name sshd -StartupType Automatic
   
   # Configure firewall
   New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
   ```

2. **Find Your IP Address:**
   ```powershell
   ipconfig
   # Look for "IPv4 Address" under your network adapter
   ```

3. **Note Your Username:**
   ```powershell
   echo $env:USERNAME
   ```

### Laptop Setup (Import Profile)

Once you have the JSON file on your laptop:

```powershell
# Import the profile
pssh import-profile C:\path\to\desktop_profile.json

# Optional: Rename the profile
pssh import-profile desktop_profile.json --name my-desktop

# List all profiles to verify
pssh list-profiles

# Connect
pssh connect my-desktop
```

---

## 🔐 Authentication Methods

### Method 1: Password Authentication

**On Desktop:**
- No additional setup needed
- Uses your Windows/Linux user password

**On Laptop:**
- Will be prompted for password when connecting
- Less secure, but simpler

### Method 2: SSH Key Authentication (Recommended)

**On Desktop (during setup):**
```
❓ Generate SSH keys? (y/n): y
```

This creates:
- `~/.ssh/id_ed25519` (private key)
- `~/.ssh/id_ed25519.pub` (public key)

**On Laptop:**

1. **Copy the public key to your desktop:**
   ```powershell
   # On laptop, get your public key
   cat ~/.ssh/id_ed25519.pub
   ```

2. **On desktop, add to authorized keys:**
   ```powershell
   # Windows
   echo "your-public-key-content" >> C:\Users\AMD\.ssh\authorized_keys
   
   # Linux/macOS
   echo "your-public-key-content" >> ~/.ssh/authorized_keys
   ```

3. **Update profile on laptop:**
   Edit the imported profile to include your key:
   ```powershell
   # The import-profile command should automatically include the key_file
   # from the JSON configuration
   ```

---

## 🚀 Usage Examples

### Basic Connection

```powershell
# Connect to desktop
pssh connect my-desktop

# Execute a command
pssh exec my-desktop "dir C:\Users"

# Disconnect
pssh disconnect
```

### File Transfer

```powershell
# Upload file to desktop
pssh upload local-file.txt my-desktop:C:\Users\AMD\Desktop\

# Download file from desktop
pssh download my-desktop:C:\Users\AMD\Documents\report.pdf ./downloads/

# Upload directory (if supported)
pssh upload ./project my-desktop:C:\Projects\
```

### List Devices

```powershell
# List all configured profiles
pssh list-profiles

# List active connections
pssh list-connections

# List active sessions
pssh list-sessions
```

---

## ⚙️ Configuration Files

### Desktop Configuration File

**Location:** `C:\Users\AMD\.personal-ssh-cli\<hostname>_profile.json`

**Example:**
```json
{
  "profile_name": "my-desktop",
  "host": "192.168.1.100",
  "hostname": "DESKTOP-PC",
  "username": "AMD",
  "port": 22,
  "auth_method": "key",
  "key_file": "~/.ssh/id_ed25519",
  "description": "Windows - DESKTOP-PC",
  "os_type": "Windows",
  "alternative_ips": [
    "192.168.1.100",
    "127.0.0.1"
  ]
}
```

### Laptop Configuration Files

**Location:** `C:\Users\<YourUsername>\.personal-ssh-cli\`

**Files:**
- `config.yaml` - Global settings
- `profiles.yaml` - Device profiles

**profiles.yaml Example:**
```yaml
profiles:
  my-desktop:
    host: 192.168.1.100
    username: AMD
    port: 22
    auth_method: key
    key_file: C:\Users\AMD\.ssh\id_ed25519
    description: "Windows - DESKTOP-PC"
    
tags:
  home: [my-desktop]
  servers: []
  work: []
```

---

## 🔧 Troubleshooting

### Issue: "Connection refused"

**Solutions:**
1. Check if SSH server is running on desktop:
   ```powershell
   # Windows
   Get-Service sshd
   
   # If not running
   Start-Service sshd
   ```

2. Check firewall:
   ```powershell
   # Verify SSH port 22 is open
   Get-NetFirewallRule -DisplayName "*ssh*"
   ```

3. Verify IP address:
   ```powershell
   # On desktop
   ipconfig
   
   # Test connectivity from laptop
   ping 192.168.1.100
   ```

### Issue: "Permission denied"

**Solutions:**
1. Verify username is correct
2. Check password authentication is enabled on desktop
3. For key-based auth, ensure public key is in `~/.ssh/authorized_keys`

### Issue: "Host key verification failed"

**Solutions:**
1. Remove old host key:
   ```powershell
   ssh-keygen -R 192.168.1.100
   ```

2. Connect manually once to accept new key:
   ```powershell
   ssh AMD@192.168.1.100
   ```

### Issue: Setup script needs Administrator

**On Windows:**
```powershell
# Right-click PowerShell and "Run as Administrator"
cd D:\AMD\projects\System-Manager
python setup_ssh_server.py
```

---

## 🌐 Network Considerations

### Local Network (Same WiFi/Ethernet)

- Use local IP address (e.g., `192.168.1.100`)
- Fast and secure within your home network
- No internet required

### Remote Access (Different Networks)

**Option 1: Port Forwarding**
- Configure your router to forward port 22
- Use your public IP address
- Security risk - use strong authentication

**Option 2: VPN**
- Set up a VPN between networks
- Access desktop using local IP through VPN
- More secure than port forwarding

**Option 3: SSH Tunneling**
- Use an intermediate jump server
- Configure in profile with `ProxyJump`

---

## 📊 Profile Management

### Import Multiple Devices

```powershell
# Import desktop
pssh import-profile desktop_profile.json

# Import laptop (if setting up bi-directional)
pssh import-profile laptop_profile.json

# Import server
pssh import-profile server_profile.json

# List all
pssh list-profiles
```

### Update Profile

```powershell
# Delete old profile
pssh delete-profile my-desktop

# Re-import with new configuration
pssh import-profile updated_desktop_profile.json
```

### Manual Profile Editing

Edit `C:\Users\<Username>\.personal-ssh-cli\profiles.yaml`:

```yaml
profiles:
  my-desktop:
    host: 192.168.1.100  # Update IP if changed
    username: AMD
    port: 22
    auth_method: key
    key_file: C:\Users\AMD\.ssh\id_ed25519
```

---

## ✅ Verification Checklist

Before attempting to connect from laptop to desktop:

**On Desktop:**
- [ ] SSH server is installed
- [ ] SSH service is running
- [ ] Firewall allows port 22
- [ ] You know the IP address
- [ ] You know the username
- [ ] Authentication method is configured (password or key)

**On Laptop:**
- [ ] `pssh` is installed (`pip install -e .`)
- [ ] Profile is imported or manually added
- [ ] Network connectivity to desktop (can ping)
- [ ] SSH key is available (if using key auth)

**Test Connection:**
```powershell
# From laptop, test basic SSH
ssh username@desktop-ip

# If that works, use pssh
pssh connect my-desktop
```

---

## 🎓 Next Steps

Once connected, explore more features:

```powershell
# View all commands
pssh --help

# Interactive session
pssh connect my-desktop

# File synchronization
pssh upload ./project my-desktop:~/backups/

# Remote execution
pssh exec my-desktop "systeminfo"

# Multiple connections
pssh connect desktop1
pssh connect desktop2
pssh list-connections
```

---

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review logs in `~/.personal-ssh-cli/logs/`
3. Test basic SSH connectivity first
4. Verify network configuration
5. Check SSH server status on desktop

For more help:
- Check documentation in `personal-ssh-cli/documentation/`
- Review example scripts in `personal-ssh-cli/resources/examples/`
