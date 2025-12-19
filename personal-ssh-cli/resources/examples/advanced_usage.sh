#!/bin/bash
# Advanced Usage Examples for Personal SSH/SCP CLI

# Multiple device management
echo "=== Managing Multiple Devices ==="

# Add multiple devices
pssh add-profile server1 --hostname 192.168.1.10 --username admin
pssh add-profile server2 --hostname 192.168.1.20 --username admin
pssh add-profile server3 --hostname 192.168.1.30 --username admin

# Connect to all
pssh connect server1
pssh connect server2
pssh connect server3

# Check all connections
pssh list-connections

# Bulk operations
echo "=== Bulk Operations ==="

# Execute same command on multiple servers
for conn in conn_1 conn_2 conn_3; do
  echo "Checking uptime on $conn"
  pssh exec $conn "uptime"
done

# Collect logs from all servers
for i in 1 2 3; do
  echo "Downloading logs from server$i"
  pssh download conn_$i /var/log/app.log ./logs/server${i}_app.log
done

# File synchronization
echo "=== File Synchronization ==="

# Upload configuration to multiple servers
for conn in conn_1 conn_2 conn_3; do
  echo "Uploading config to $conn"
  pssh upload $conn ./config.yaml /etc/app/config.yaml --verify
done

# Backup operations
echo "=== Backup Operations ==="

# Create remote backup
pssh exec conn_1 "tar -czf /tmp/backup-$(date +%Y%m%d).tar.gz /important/data"

# Download backup
pssh download conn_1 /tmp/backup-*.tar.gz ./backups/

# Verify backup integrity
pssh exec conn_1 "sha256sum /tmp/backup-*.tar.gz"

# Monitoring
echo "=== System Monitoring ==="

# Check system resources on all servers
for conn in conn_1 conn_2 conn_3; do
  echo "=== $conn ==="
  pssh exec $conn "echo 'CPU:' && uptime"
  pssh exec $conn "echo 'Memory:' && free -h"
  pssh exec $conn "echo 'Disk:' && df -h /"
done

# Network diagnostics
echo "=== Network Diagnostics ==="

# Check connectivity between servers
pssh exec conn_1 "ping -c 3 192.168.1.20"
pssh exec conn_2 "ping -c 3 192.168.1.30"

# Security operations
echo "=== Security Operations ==="

# Update SSH keys on remote
cat ~/.ssh/id_ed25519.pub | pssh exec conn_1 "cat >> ~/.ssh/authorized_keys"

# Check for system updates
pssh exec conn_1 "sudo apt update && apt list --upgradable"

# Session management
echo "=== Session Management ==="

# View all active sessions
pssh list-sessions

# Check session history
# (View in ~/.personal-ssh-cli/sessions.json)

# Cleanup
echo "=== Cleanup ==="
pssh disconnect

echo "=== Advanced Examples Complete ==="
