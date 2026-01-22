#!/bin/bash
# Health Check Script for Fleet Manager
# Run this to quickly check if everything is working properly

echo "======================================"
echo "Fleet Manager Health Check"
echo "======================================"
echo ""

# Check if service is running
echo "[1/5] Checking service status..."
if systemctl is-active --quiet fleet-manager; then
    echo "✓ Service is running"
else
    echo "✗ Service is NOT running"
    echo "  Start with: sudo systemctl start fleet-manager"
fi
echo ""

# Check if service is enabled
echo "[2/5] Checking auto-start configuration..."
if systemctl is-enabled --quiet fleet-manager; then
    echo "✓ Service will auto-start on boot"
else
    echo "✗ Service will NOT auto-start on boot"
    echo "  Enable with: sudo systemctl enable fleet-manager"
fi
echo ""

# Check if port is listening
echo "[3/5] Checking web server port..."
if netstat -tuln 2>/dev/null | grep -q ":5001 "; then
    echo "✓ Web server is listening on port 5001"
elif ss -tuln 2>/dev/null | grep -q ":5001 "; then
    echo "✓ Web server is listening on port 5001"
else
    echo "✗ Web server is NOT listening on port 5001"
    echo "  Check logs: tail -50 ~/home-mining-fleet-manager/logs/fleet-manager.error.log"
fi
echo ""

# Check database
echo "[4/5] Checking database..."
if [ -f ~/home-mining-fleet-manager/fleet.db ]; then
    DB_SIZE=$(du -h ~/home-mining-fleet-manager/fleet.db | cut -f1)
    echo "✓ Database exists (Size: $DB_SIZE)"
else
    echo "✗ Database NOT found"
    echo "  Initialize with: cd ~/home-mining-fleet-manager && python3 -c 'from database import Database; import config; Database(config.DATABASE_PATH)'"
fi
echo ""

# Check system resources
echo "[5/5] Checking system resources..."
MEMORY_FREE=$(free -h | awk '/^Mem:/ {print $4}')
DISK_FREE=$(df -h ~ | awk 'NR==2 {print $4}')
CPU_TEMP=$(vcgencmd measure_temp 2>/dev/null | cut -d= -f2 || echo "N/A")

echo "  Free Memory: $MEMORY_FREE"
echo "  Free Disk: $DISK_FREE"
echo "  CPU Temp: $CPU_TEMP"

if [ "$CPU_TEMP" != "N/A" ]; then
    TEMP_NUM=$(echo $CPU_TEMP | sed 's/°C//' | sed "s/'C//")
    if (( $(echo "$TEMP_NUM > 80" | bc -l) )); then
        echo "  ⚠ WARNING: CPU temperature is high!"
    fi
fi
echo ""

# Get IP address
echo "======================================"
echo "Access Information"
echo "======================================"
IP_ADDR=$(hostname -I | awk '{print $1}')
echo "Dashboard URL: http://$IP_ADDR:5001"
echo ""

# Show recent errors (if any)
echo "======================================"
echo "Recent Errors (if any)"
echo "======================================"
if [ -f ~/home-mining-fleet-manager/logs/fleet-manager.error.log ]; then
    ERROR_COUNT=$(wc -l < ~/home-mining-fleet-manager/logs/fleet-manager.error.log)
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo "Found $ERROR_COUNT lines in error log"
        echo "Last 5 errors:"
        tail -5 ~/home-mining-fleet-manager/logs/fleet-manager.error.log
    else
        echo "✓ No errors logged"
    fi
else
    echo "Error log not found"
fi
echo ""

echo "======================================"
echo "Health Check Complete"
echo "======================================"
echo ""
echo "For detailed logs, run:"
echo "  sudo journalctl -u fleet-manager -n 50"
echo ""
