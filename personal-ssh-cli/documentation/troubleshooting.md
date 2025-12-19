# Troubleshooting Guide

Common issues and their solutions.

## Connection Issues

### Cannot connect to device

**Symptoms:**
- Connection timeout
- "Connection refused" error
- "No route to host" error

**Solutions:**

1. **Check network connectivity:**
```bash
ping <hostname>
traceroute <hostname>
```

2. **Verify SSH service is running:**
```bash
# On the remote device
sudo systemctl status sshd    # Linux
sudo service ssh status        # Alternative
```

3. **Check firewall rules:**
```bash
# On remote device
sudo ufw status                # Ubuntu/Debian
sudo firewall-cmd --list-all   # RHEL/CentOS
```

4. **Verify correct port:**
- Default SSH port is 22
- Check if custom port is configured
- Update profile with correct port

5. **Test with standard SSH:**
```bash
ssh -v username@hostname
```
The verbose output will show where the connection fails.

---

### Authentication failures

**Symptoms:**
- "Permission denied (publickey)"
- "Authentication failed"
- Repeated password prompts

**Solutions:**

1. **Check SSH key permissions:**
```bash
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
chmod 700 ~/.ssh
```

2. **Verify public key on remote:**
```bash
# On remote device
cat ~/.ssh/authorized_keys
```
Your public key should be present.

3. **Copy public key to remote:**
```bash
ssh-copy-id username@hostname
```

4. **Test key authentication:**
```bash
ssh -i ~/.ssh/id_ed25519 username@hostname
```

5. **Check SELinux (RHEL/CentOS):**
```bash
restorecon -R ~/.ssh
```

---

### Host key verification failed

**Symptoms:**
- "WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!"
- "Host key verification failed"

**Solutions:**

1. **If this is expected (e.g., reinstalled server):**
```bash
ssh-keygen -R hostname
```

2. **If unexpected:** This could indicate a security issue:
- Verify you're connecting to the correct device
- Contact the device administrator
- Check for network issues or MITM attacks

3. **Update whitelist:**
```bash
# Remove old entry and reconnect to update
rm ~/.personal-ssh-cli/whitelist.json
pssh connect profile-name
```

---

## File Transfer Issues

### Upload/Download fails

**Symptoms:**
- Transfer interrupted
- Checksum verification failed
- Permission denied

**Solutions:**

1. **Check disk space:**
```bash
# On remote
pssh exec conn_1 "df -h"

# Locally
df -h
```

2. **Verify permissions:**
```bash
# Check remote directory permissions
pssh exec conn_1 "ls -ld /target/directory"

# Check local file permissions
ls -l /local/file
```

3. **Try without verification:**
```bash
pssh upload conn_1 file.txt /remote/ --no-verify
```

4. **Check file paths:**
- Ensure paths are correct
- Use absolute paths when possible
- Quote paths with spaces

5. **Test with standard SCP:**
```bash
scp file.txt username@hostname:/path/
```

---

### Slow transfer speeds

**Symptoms:**
- Transfers taking much longer than expected
- Low transfer speeds

**Solutions:**

1. **Enable compression:**
Edit `~/.personal-ssh-cli/config.yaml`:
```yaml
performance:
  compression: true
```

2. **Check network bandwidth:**
```bash
# Test with iperf if available
iperf -c hostname
```

3. **Disable verification for large files:**
```bash
pssh upload conn_1 largefile.iso /remote/ --no-verify
```

4. **Check network latency:**
```bash
ping -c 10 hostname
```

5. **Use SSH multiplexing:**
Edit `~/.personal-ssh-cli/config.yaml`:
```yaml
performance:
  ssh_multiplexing: true
```

---

## Configuration Issues

### Configuration file errors

**Symptoms:**
- "Failed to load configuration"
- YAML parse errors
- Invalid settings

**Solutions:**

1. **Validate YAML syntax:**
```bash
python3 -c "import yaml; yaml.safe_load(open('~/.personal-ssh-cli/config.yaml'))"
```

2. **Reset to defaults:**
```bash
rm ~/.personal-ssh-cli/config.yaml
pssh setup
```

3. **Check file permissions:**
```bash
ls -la ~/.personal-ssh-cli/
```
Configuration directory should be readable and writable.

---

### Profile not found

**Symptoms:**
- "Profile 'name' not found"

**Solutions:**

1. **List available profiles:**
```bash
pssh list-profiles
```

2. **Check profile name spelling:**
- Profile names are case-sensitive
- Check for typos

3. **Recreate profile:**
```bash
pssh add-profile name --hostname host --username user
```

---

## Performance Issues

### High memory usage

**Symptoms:**
- System slowdown
- Out of memory errors

**Solutions:**

1. **Check active connections:**
```bash
pssh list-connections
```

2. **Disconnect idle connections:**
```bash
pssh disconnect
```

3. **Monitor system resources:**
```bash
# Check memory usage
free -h

# Check process memory
ps aux | grep python
```

4. **Adjust session settings:**
Edit `~/.personal-ssh-cli/config.yaml`:
```yaml
settings:
  session_history_size: 100  # Reduce if needed
```

---

### Slow startup time

**Symptoms:**
- Application takes long to start

**Solutions:**

1. **Clean old sessions:**
```bash
# Sessions older than 7 days are auto-cleaned
# Manually remove if needed
rm ~/.personal-ssh-cli/sessions.json
```

2. **Check log file size:**
```bash
ls -lh ~/.personal-ssh-cli/logs/
```

3. **Clear old logs:**
```bash
# Backup first if needed
rm ~/.personal-ssh-cli/logs/audit.log
```

---

## System-Specific Issues

### Windows Issues

**Problem:** SSH not found
```bash
# Install OpenSSH on Windows
Add-WindowsCapability -Online -Name OpenSSH.Client
```

**Problem:** Path issues
- Use forward slashes in paths when possible
- Quote paths with spaces: `"C:/Program Files/file.txt"`

---

### Linux Issues

**Problem:** Permission denied on operations
```bash
# Check if SSH agent is running
eval $(ssh-agent)
ssh-add ~/.ssh/id_ed25519
```

---

### macOS Issues

**Problem:** "Operation not permitted" errors
- Grant Terminal full disk access in System Preferences
- Security & Privacy → Privacy → Full Disk Access

---

## Logging and Debugging

### Enable verbose logging

Edit `~/.personal-ssh-cli/config.yaml`:
```yaml
settings:
  log_level: debug
```

### View audit logs

```bash
tail -f ~/.personal-ssh-cli/logs/audit.log
```

### Test SSH connection manually

```bash
ssh -vvv username@hostname
```
Triple verbosity shows detailed connection process.

### Check system information

```bash
# Python version
python3 --version

# SSH version
ssh -V

# System info
uname -a
```

---

## Getting Additional Help

1. **Check documentation:**
   - User Guide: `documentation/user_guide.md`
   - Command Reference: `documentation/command_reference.md`

2. **Review audit logs:**
   - Location: `~/.personal-ssh-cli/logs/audit.log`
   - Contains detailed event information

3. **Test with standard tools:**
   - Use `ssh` and `scp` commands directly
   - Isolate whether issue is with tool or environment

4. **Common error patterns:**
   - Connection issues: Check network and SSH service
   - Authentication: Verify keys and permissions
   - Transfers: Check disk space and permissions
   - Performance: Check network bandwidth and system resources

## Emergency Recovery

### Reset entire configuration

```bash
# Backup first
mv ~/.personal-ssh-cli ~/.personal-ssh-cli.backup

# Reinitialize
pssh setup
```

### Recover from corrupted files

```bash
# Remove problematic file
rm ~/.personal-ssh-cli/sessions.json

# Or specific config
rm ~/.personal-ssh-cli/config.yaml

# Reinitialize
pssh setup
```
