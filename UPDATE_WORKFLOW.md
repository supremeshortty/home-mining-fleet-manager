# Update Workflow - Keeping Raspberry Pi in Sync

This document explains how to keep your Raspberry Pi running the latest version of DirtySats fleet manager.

## Overview

- **Local folder on Mac:** `home-mining-fleet-manager-main`
- **GitHub repository:** `dirtysats` (https://github.com/USERNAME/dirtysats.git)
- **Raspberry Pi location:** `/home/USERNAME/home-mining-fleet-manager`
- **Raspberry Pi credentials:** Stored in `pi-config.sh` (excluded from git)

## Initial Setup

Before you can update the Pi, you need to configure your credentials:

**One-time setup:**
```bash
cd ~/Desktop/Coding/Hash/home-mining-fleet-manager-main
cp pi-config.sh.template pi-config.sh
nano pi-config.sh  # Edit with your Pi's credentials
```

The `pi-config.sh` file is excluded from git and will never be committed. It contains:
- PI_USER: Your Raspberry Pi username
- PI_HOST: Your Raspberry Pi IP address
- PI_PASSWORD: Your Raspberry Pi password
- PI_DIR: Installation directory on the Pi

## Two Ways to Update the Pi

### Method 1: Push from Mac (Recommended for development)

Use this when you're actively developing and want to quickly push changes to the Pi.

**From your Mac:**
```bash
cd ~/Desktop/Coding/Hash/home-mining-fleet-manager-main
./update-pi.sh
```

This will:
1. Transfer all files to the Pi
2. Update dependencies if needed
3. Restart the service
4. Verify it's running

**No need to commit/push to GitHub first** - this directly syncs your local files to the Pi.

### Method 2: Pull from GitHub (Recommended for production updates)

Use this when you've pushed changes to GitHub and want the Pi to pull them.

**Step 1: Push changes from Mac to GitHub**
```bash
cd ~/Desktop/Coding/Hash/home-mining-fleet-manager-main
git add .
git commit -m "Your update message"
git push origin main
```

**Step 2: Update Pi from GitHub**
```bash
ssh USERNAME@PI_IP
cd ~/home-mining-fleet-manager
./update-from-git.sh
```

Or run it remotely from your Mac:
```bash
ssh USERNAME@PI_IP 'cd ~/home-mining-fleet-manager && ./update-from-git.sh'
```

## Typical Workflow

### During Active Development
1. Make changes on your Mac
2. Run `./update-pi.sh` to push to Pi
3. Test on Pi
4. Repeat until satisfied
5. Commit and push to GitHub when ready

### For Production Updates
1. Make changes on your Mac
2. Test locally
3. Commit and push to GitHub
4. SSH to Pi and run `./update-from-git.sh`

## Important Notes

### The Service Keeps Running
- The fleet manager service runs 24/7 on the Pi
- When you update, the service briefly restarts (2-3 seconds)
- It automatically comes back up
- No manual intervention needed

### What Gets Updated
When you run updates, these are transferred/updated:
- All Python files (*.py)
- Shell scripts (*.sh)
- Documentation (*.md)
- Configuration files
- Templates and static files
- Miner modules
- Database modules

**What DOESN'T get updated:**
- The database file (`fleet.db`) - your data is preserved
- Virtual environment (only if requirements.txt changes)
- System service configuration (unless you specifically update it)

## Verifying Updates

After updating, check that everything is working:

**Check service status:**
```bash
ssh USERNAME@PI_IP 'sudo systemctl status fleet-manager'
```

**View recent logs:**
```bash
ssh USERNAME@PI_IP 'sudo journalctl -u fleet-manager -n 30'
```

**Access dashboard:**
Open http://10.0.0.12:5001 in your browser

## Troubleshooting

### Update Script Fails
```bash
# Check Pi connectivity
ping 10.0.0.12

# SSH manually to debug
ssh USERNAME@PI_IP
```

### Service Won't Start After Update
```bash
# View error logs
ssh USERNAME@PI_IP 'sudo journalctl -u fleet-manager -n 50'

# Check for Python errors
ssh USERNAME@PI_IP 'cd ~/home-mining-fleet-manager && source venv/bin/activate && python3 -c "import app"'
```

### Database Issues After Update
```bash
# Restore from backup (if needed)
ssh USERNAME@PI_IP
cp ~/home-mining-fleet-manager/fleet.db.backup ~/home-mining-fleet-manager/fleet.db
sudo systemctl restart fleet-manager
```

## Best Practices

1. **Always test locally first** before pushing to production Pi
2. **Commit to GitHub regularly** to have version history
3. **Use Method 1 (push from Mac)** during development for speed
4. **Use Method 2 (pull from Git)** for official releases
5. **Keep backups** of your database before major updates
6. **Monitor logs** after updates to catch any issues early

## Quick Reference Commands

```bash
# Push update from Mac to Pi
cd ~/Desktop/Coding/Hash/home-mining-fleet-manager-main && ./update-pi.sh

# Pull update on Pi from GitHub
ssh USERNAME@PI_IP 'cd ~/home-mining-fleet-manager && ./update-from-git.sh'

# Check service status
ssh USERNAME@PI_IP 'sudo systemctl status fleet-manager'

# View live logs
ssh USERNAME@PI_IP 'sudo journalctl -u fleet-manager -f'

# Restart service manually
ssh USERNAME@PI_IP 'sudo systemctl restart fleet-manager'

# Backup database before update
ssh USERNAME@PI_IP 'cp ~/home-mining-fleet-manager/fleet.db ~/fleet-backup-$(date +%Y%m%d).db'
```

## Automatic Updates (Optional)

If you want the Pi to automatically pull updates from GitHub daily:

```bash
ssh USERNAME@PI_IP
crontab -e

# Add this line to update daily at 3 AM:
0 3 * * * cd /home/nathanshortt/home-mining-fleet-manager && ./update-from-git.sh >> /home/nathanshortt/update.log 2>&1
```

**Warning:** Only enable automatic updates if you're confident in your CI/CD process. Otherwise, stick with manual updates.

---

## Summary

Your Pi is set up to:
- ✅ Run the fleet manager 24/7
- ✅ Auto-restart on boot
- ✅ Auto-restart if it crashes
- ✅ Easy updates via `./update-pi.sh` from Mac
- ✅ Pull from GitHub via `./update-from-git.sh` on Pi
- ✅ Preserve your data during updates

**The system will always be running and you can update it anytime!**
