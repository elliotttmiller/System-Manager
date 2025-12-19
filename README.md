# 🖥️ System Manager

**A Professional-Grade SSH Management Suite for Personal Infrastructure**

> Transform your multi-device workflow with intelligent SSH management, automated server monitoring, and seamless remote control—all from one powerful terminal interface.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Core Features](#-core-features)
- [Documentation](#-documentation)
- [Architecture](#-architecture)
- [Platform Support](#-platform-support)
- [Security](#-security)
- [Performance](#-performance)

---

## 🎯 Overview

**System Manager** is a comprehensive Python-based SSH management solution designed for power users managing multiple personal devices. Whether you're connecting from your laptop to your desktop, managing home servers, or coordinating across development environments, System Manager provides enterprise-grade tools with personal-infrastructure simplicity.

---

## ✨ Key Features

- **Device Profile Management**: Save and manage SSH connection profiles for all your devices.
- **Seamless Connections**: Quick SSH connections with automatic authentication.
- **Smart File Transfers**: SCP/SFTP transfers with integrity verification and resume capability.
- **Session Management**: Persistent sessions that survive application restarts.
- **Security First**: SSH key-based authentication, host key verification, and encrypted credential storage.
- **Rich Terminal UI**: Color-coded output, progress bars, and interactive menus.
- **Cross-Platform**: Works on Windows, Linux, and macOS.
- **Offline-First**: Full functionality without internet connectivity.

---

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/elliotttmiller/System-Manager.git
   cd System-Manager
   ```
2. Install the package:
   ```bash
   pip install -e .
   ```
3. Run the setup wizard:
   ```bash
   pssh setup
   ```

---

## 🚀 Quick Start

### Add a Device Profile
```bash
pssh add-profile home-server --hostname 192.168.1.100 --username myuser
```

### Connect to the Device
```bash
pssh connect home-server
```

### Execute a Command
```bash
pssh exec conn_1 "ls -la"
```

### Transfer Files
```bash
pssh upload conn_1 /local/file.txt /remote/file.txt
pssh download conn_1 /remote/log.txt /local/log.txt
```

### List Connections and Sessions
```bash
pssh list-connections
pssh list-sessions
```

---

## 🔑 Core Features

### Connection Management
- Profile-based connections with custom labels.
- Quick connect with auto-discovery of SSH-enabled devices.
- Multi-session support with session persistence.

### File Transfer
- Bidirectional transfers with progress tracking.
- Integrity verification and resume capability.
- Batch operations and smart compression.

### Server Actions
- Start/stop/restart SSH server.
- Enable/disable autostart on boot.
- View and validate SSH configuration.
- Access SSH server logs.

### System Monitoring
- Real-time resource tracking (CPU, memory, disk, network).
- Service monitoring and diagnostics.

---

## 📚 Documentation

- **[User Guide](personal-ssh-cli/documentation/user_guide.md)**: Complete usage instructions.
- **[Command Reference](personal-ssh-cli/documentation/command_reference.md)**: Full command listing with examples.
- **[Troubleshooting](personal-ssh-cli/documentation/troubleshooting.md)**: Common issue resolution.

---

## 🏗️ Architecture

System Manager uses a modular architecture with clear separation between local and remote operations:

- **Local Features**: System monitoring, file management, network tools, and security auditing.
- **Remote Features**: Real-time resource tracking, server actions, file management, and process control.
- **Security Modules**: SSH key management, device whitelisting, and audit logging.

---

## 💻 Platform Support

- **Windows**: Full support with PowerShell integration.
- **Linux**: Native support for all major distributions.
- **macOS**: Full support with Homebrew integration.
- **Remote Devices**: Linux and macOS remote device management.

---

## 🔒 Security

- AES-256 encrypted credential storage.
- SSH key-based authentication and host key verification.
- Local audit logging for all activities.
- No cloud dependencies or external API calls.

---

## 📊 Performance

- **Startup Time**: < 3 seconds.
- **Optimized Transfers**: Smart compression and caching.
- **Low Resource Usage**: Minimal CPU and memory footprint.

---

**System Manager**: Simplifying SSH management for power users. 🚀
