# Raspberry Pi Setup Guide

This guide will help you set up the Bitcoin Mining Fleet Manager to run continuously on your Raspberry Pi with automatic startup on boot.

## Prerequisites

- Raspberry Pi (3, 4, or 5 recommended)
- Raspberry Pi OS (formerly Raspbian) installed
- Network connection (WiFi or Ethernet)
- SSH access or direct access to the Pi

## Quick Install (Recommended)

### Step 1: Transfer Files to Raspberry Pi

You have several options:

**Option A: Using Git (Recommended)**
```bash
ssh pi@<raspberry-pi-ip>
cd ~
git clone <your-repository-url>
cd home-mining-fleet-manager
```

**Option B: Using SCP from your computer**
```bash
# From your Mac/PC, run:
scp -r home-mining-fleet-manager-main pi@<raspberry-pi-ip>:~/home-mining-fleet-manager
```

**Option C: Using USB Drive**
- Copy the `home-mining-fleet-manager-main` folder to a USB drive
- Plug into Raspberry Pi
- Copy to home directory: `cp -r /media/usb/home-mining-fleet-manager-main ~/home-mining-fleet-manager`

### Step 2: Run Installation Script

```bash
cd ~/home-mining-fleet-manager
./install-raspberry-pi.sh
```

The script will:
1. Check Python installation
2. Create virtual environment
3. Install dependencies
4. Initialize database
5. Install and enable systemd service
6. Configure log rotation
7. Start the service automatically

That's it! The fleet manager is now running and will auto-start on every boot.

---

## Service Management

Once installed, manage the fleet manager service with these commands:

### Check Service Status
```bash
sudo systemctl status fleet-manager
```

### Start Service
```bash
sudo systemctl start fleet-manager
```

### Stop Service
```bash
sudo systemctl stop fleet-manager
```

### Restart Service
```bash
sudo systemctl restart fleet-manager
```

### Disable Auto-Start (if needed)
```bash
sudo systemctl disable fleet-manager
```

### Re-Enable Auto-Start
```bash
sudo systemctl enable fleet-manager
```

---

## Viewing Logs

### Real-Time Service Logs
```bash
sudo journalctl -u fleet-manager -f
```

### Application Logs
```bash
tail -f ~/home-mining-fleet-manager/logs/fleet-manager.log
```

### Error Logs
```bash
tail -f ~/home-mining-fleet-manager/logs/fleet-manager.error.log
```

### View Last 100 Lines
```bash
sudo journalctl -u fleet-manager -n 100
```

### View Logs from Today
```bash
sudo journalctl -u fleet-manager --since today
```

---

## Configuration

### Update Network Subnet

Edit the config file:
```bash
nano ~/home-mining-fleet-manager/config.py
```

Change the network subnet to match your network:
```python
NETWORK_SUBNET = "192.168.1.0/24"  # Change to your network
```

After making changes, restart the service:
```bash
sudo systemctl restart fleet-manager
```

### Change Web Server Port

In `config.py`:
```python
FLASK_PORT = 5001  # Change to desired port
```

Then restart:
```bash
sudo systemctl restart fleet-manager
```

---

## Accessing the Dashboard

### From Same Network
Open a web browser on any device on your network:
```
http://<raspberry-pi-ip>:5001
```

### Find Your Raspberry Pi's IP Address
```bash
hostname -I
```

### Access from Raspberry Pi Desktop
If using Raspberry Pi with desktop:
```
http://localhost:5001
```

---

## Troubleshooting

### Service Won't Start

1. **Check service status for errors:**
   ```bash
   sudo systemctl status fleet-manager
   ```

2. **Check application logs:**
   ```bash
   tail -50 ~/home-mining-fleet-manager/logs/fleet-manager.error.log
   ```

3. **Verify Python and dependencies:**
   ```bash
   cd ~/home-mining-fleet-manager
   source venv/bin/activate
   python3 -c "import flask, requests; print('Dependencies OK')"
   ```

### Can't Access Dashboard from Other Devices

1. **Check if service is running:**
   ```bash
   sudo systemctl status fleet-manager
   ```

2. **Verify the port is listening:**
   ```bash
   sudo netstat -tulpn | grep 5001
   ```

3. **Check firewall (if enabled):**
   ```bash
   sudo ufw status
   # If firewall is active, allow the port:
   sudo ufw allow 5001/tcp
   ```

4. **Verify Pi's IP address:**
   ```bash
   hostname -I
   ```

### Service Crashes or Restarts Frequently

1. **Check error logs:**
   ```bash
   sudo journalctl -u fleet-manager -n 200
   ```

2. **Check system resources:**
   ```bash
   # Memory usage
   free -h

   # CPU temperature (Pi may throttle if overheating)
   vcgencmd measure_temp
   ```

3. **Check disk space:**
   ```bash
   df -h
   ```

### Miners Not Being Discovered

1. **Verify network subnet in config:**
   ```bash
   nano ~/home-mining-fleet-manager/config.py
   ```
   Make sure `NETWORK_SUBNET` matches your network.

2. **Test connectivity to a miner:**
   ```bash
   ping <miner-ip>
   curl http://<miner-ip>/api/system/info  # For Bitaxe
   ```

3. **Check Pi can reach the miners' network:**
   ```bash
   ip addr show
   ip route
   ```

---

## Updating the Application

### Pull Latest Changes (if using Git)
```bash
cd ~/home-mining-fleet-manager
git pull
sudo systemctl restart fleet-manager
```

### Manual Update
1. Stop the service:
   ```bash
   sudo systemctl stop fleet-manager
   ```

2. Update files (copy new files via SCP or USB)

3. Update dependencies:
   ```bash
   cd ~/home-mining-fleet-manager
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Restart service:
   ```bash
   sudo systemctl start fleet-manager
   ```

---

## Performance Optimization

### Recommended Raspberry Pi Settings

1. **Increase swap if you have < 2GB RAM:**
   ```bash
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile
   # Set CONF_SWAPSIZE=1024
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

2. **Keep system updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **Enable overclock (Pi 4 only, optional):**
   ```bash
   sudo raspi-config
   # Performance Options > Overclock
   ```

### Monitoring System Resources

```bash
# Install htop for better monitoring
sudo apt install htop
htop

# Check temperature
watch -n 1 vcgencmd measure_temp
```

---

## Backup and Recovery

### Backup Database
```bash
cp ~/home-mining-fleet-manager/fleet.db ~/fleet.db.backup
```

### Automated Backup Script
Create a backup script:
```bash
nano ~/backup-fleet.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="$HOME/fleet-backups"
mkdir -p "$BACKUP_DIR"
DATE=$(date +%Y%m%d_%H%M%S)
cp ~/home-mining-fleet-manager/fleet.db "$BACKUP_DIR/fleet_$DATE.db"
# Keep only last 7 days
find "$BACKUP_DIR" -name "fleet_*.db" -mtime +7 -delete
```

Make executable and add to crontab:
```bash
chmod +x ~/backup-fleet.sh
crontab -e
# Add: 0 2 * * * /home/pi/backup-fleet.sh
```

### Restore Database
```bash
sudo systemctl stop fleet-manager
cp ~/fleet.db.backup ~/home-mining-fleet-manager/fleet.db
sudo systemctl start fleet-manager
```

---

## Uninstalling

To completely remove the fleet manager:

```bash
# Stop and disable service
sudo systemctl stop fleet-manager
sudo systemctl disable fleet-manager

# Remove service file
sudo rm /etc/systemd/system/fleet-manager.service
sudo systemctl daemon-reload

# Remove log rotation
sudo rm /etc/logrotate.d/fleet-manager

# Remove application directory
rm -rf ~/home-mining-fleet-manager

# (Optional) Remove backups
rm -rf ~/fleet-backups
```

---

## Security Considerations

### Change Default Credentials
If you add authentication in the future, make sure to change default credentials.

### Firewall Setup
```bash
# Install UFW (if not installed)
sudo apt install ufw

# Allow SSH
sudo ufw allow ssh

# Allow fleet manager port
sudo ufw allow 5001/tcp

# Enable firewall
sudo ufw enable
```

### Access from Internet (Not Recommended)
For security reasons, it's not recommended to expose the fleet manager directly to the internet. If you need remote access, use:

- **SSH Tunnel:**
  ```bash
  ssh -L 5001:localhost:5001 pi@<raspberry-pi-ip>
  # Then access http://localhost:5001 on your computer
  ```

- **VPN:** Set up a VPN to your home network (WireGuard, OpenVPN, etc.)

- **Tailscale:** Easy mesh VPN solution
  ```bash
  curl -fsSL https://tailscale.com/install.sh | sh
  sudo tailscale up
  ```

---

## Advanced Configuration

### Running on Different Port
Edit config.py and change `FLASK_PORT`, then restart.

### Running Multiple Instances
To run multiple fleet managers (different subnets):
1. Clone to different directory
2. Edit config.py with different PORT and SUBNET
3. Create new service file with different name
4. Install and enable the new service

### Scheduled Tasks
Add maintenance tasks to crontab:
```bash
crontab -e
```

Example tasks:
```bash
# Restart service daily at 3 AM
0 3 * * * sudo systemctl restart fleet-manager

# Clear old logs monthly
0 0 1 * * find ~/home-mining-fleet-manager/logs -name "*.log.*" -mtime +30 -delete
```

---

## Getting Help

If you encounter issues:

1. Check the logs first (see Viewing Logs section)
2. Verify configuration in `config.py`
3. Test network connectivity to miners
4. Check system resources (RAM, CPU, disk space)
5. Review Raspberry Pi system logs: `sudo dmesg | tail -50`

---

## Summary of Key Commands

```bash
# Service management
sudo systemctl status fleet-manager      # Check status
sudo systemctl restart fleet-manager     # Restart
sudo journalctl -u fleet-manager -f      # View live logs

# Application logs
tail -f ~/home-mining-fleet-manager/logs/fleet-manager.log

# Find IP address
hostname -I

# Edit configuration
nano ~/home-mining-fleet-manager/config.py

# Update application
cd ~/home-mining-fleet-manager
git pull
sudo systemctl restart fleet-manager
```

---

**Your fleet manager is now set up to run 24/7 on your Raspberry Pi!**
