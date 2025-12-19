#!/bin/bash
# Basic Usage Examples for Personal SSH/SCP CLI

# Setup (first time only)
echo "=== Initial Setup ==="
pssh setup

# Add device profiles
echo "=== Adding Device Profiles ==="
pssh add-profile home-server \
  --hostname 192.168.1.100 \
  --username admin \
  --key-file ~/.ssh/id_ed25519

pssh add-profile work-laptop \
  --hostname work.example.com \
  --username user \
  --port 22

# List all profiles
echo "=== List Profiles ==="
pssh list-profiles

# Connect to a device
echo "=== Connecting ==="
pssh connect home-server

# List active connections
echo "=== Active Connections ==="
pssh list-connections

# Execute commands
echo "=== Execute Commands ==="
pssh exec conn_1 "uptime"
pssh exec conn_1 "df -h"
pssh exec conn_1 "ls -la ~"

# Upload files
echo "=== Upload Files ==="
pssh upload conn_1 /local/document.pdf ~/documents/
pssh upload conn_1 ./backup.tar.gz /backups/

# Download files
echo "=== Download Files ==="
pssh download conn_1 /var/log/syslog ./logs/
pssh download conn_1 ~/report.txt ./reports/

# List sessions
echo "=== List Sessions ==="
pssh list-sessions

# Cleanup
echo "=== Disconnect ==="
pssh disconnect

echo "=== Done ==="
