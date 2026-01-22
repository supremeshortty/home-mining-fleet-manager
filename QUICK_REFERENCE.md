# Quick Reference - Fleet Manager Commands

## One-Time Setup
```bash
# Transfer files to Pi and install
scp -r home-mining-fleet-manager-main pi@<pi-ip>:~/home-mining-fleet-manager
ssh pi@<pi-ip>
cd ~/home-mining-fleet-manager
./install-raspberry-pi.sh
```

## Daily Use

### Check Status
```bash
sudo systemctl status fleet-manager
```

### View Live Logs
```bash
sudo journalctl -u fleet-manager -f
```

### Restart Service
```bash
sudo systemctl restart fleet-manager
```

### Access Dashboard
```
http://<raspberry-pi-ip>:5001
```

## Configuration

### Edit Settings
```bash
nano ~/home-mining-fleet-manager/config.py
# Then restart:
sudo systemctl restart fleet-manager
```

### Common Settings to Change
```python
NETWORK_SUBNET = "192.168.1.0/24"    # Your network
FLASK_PORT = 5001                     # Web interface port
UPDATE_INTERVAL = 30                  # Seconds between updates
```

## Troubleshooting

### Service Won't Start
```bash
sudo systemctl status fleet-manager           # Check status
tail -50 ~/home-mining-fleet-manager/logs/fleet-manager.error.log
```

### Can't Access Dashboard
```bash
hostname -I                          # Find Pi's IP
sudo netstat -tulpn | grep 5001     # Check if port is listening
```

### Miners Not Found
```bash
# Edit config to match your network
nano ~/home-mining-fleet-manager/config.py
# Test connectivity
ping <miner-ip>
```

## Maintenance

### Update Application
```bash
cd ~/home-mining-fleet-manager
git pull
sudo systemctl restart fleet-manager
```

### Backup Database
```bash
cp ~/home-mining-fleet-manager/fleet.db ~/fleet.db.backup.$(date +%Y%m%d)
```

### View System Resources
```bash
free -h                    # Memory
df -h                      # Disk space
vcgencmd measure_temp      # CPU temperature
```

## Stop/Start Service

### Stop
```bash
sudo systemctl stop fleet-manager
```

### Start
```bash
sudo systemctl start fleet-manager
```

### Disable Auto-Start
```bash
sudo systemctl disable fleet-manager
```

### Enable Auto-Start
```bash
sudo systemctl enable fleet-manager
```

---

**Dashboard URL:** `http://<your-pi-ip>:5001`
**Logs:** `~/home-mining-fleet-manager/logs/`
**Config:** `~/home-mining-fleet-manager/config.py`
