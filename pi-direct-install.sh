#!/bin/bash
# Direct installation script for Raspberry Pi
# Run this script ON the Raspberry Pi itself

set -e

echo "========================================="
echo "Fleet Manager - Direct Pi Installation"
echo "========================================="
echo ""
echo "This will download and install the fleet manager directly on this Pi"
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "Warning: This script should be run on the Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create installation directory
INSTALL_DIR="$HOME/home-mining-fleet-manager"
echo "Installation directory: $INSTALL_DIR"

# Check if directory exists
if [ -d "$INSTALL_DIR" ]; then
    echo "Directory already exists. Backing up..."
    mv "$INSTALL_DIR" "$INSTALL_DIR.backup.$(date +%Y%m%d_%H%M%S)"
fi

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo ""
echo "[1/9] Checking Python..."
python3 --version || {
    echo "Error: Python 3 is required"
    echo "Install with: sudo apt update && sudo apt install python3 python3-venv python3-pip"
    exit 1
}

echo ""
echo "[2/9] Creating directory structure..."
mkdir -p logs
mkdir -p database
mkdir -p miners
mkdir -p static
mkdir -p templates
mkdir -p tests

echo ""
echo "[3/9] Creating requirements.txt..."
cat > requirements.txt << 'EOF'
Flask==3.0.0
requests==2.31.0
EOF

echo ""
echo "[4/9] Creating virtual environment..."
python3 -m venv venv

echo ""
echo "[5/9] Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "[6/9] Creating systemd service file..."
cat > fleet-manager.service << EOF
[Unit]
Description=Bitcoin Mining Fleet Manager (DirtySats)
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$INSTALL_DIR/venv/bin/python3 app.py
Restart=always
RestartSec=10
StandardOutput=append:$INSTALL_DIR/logs/fleet-manager.log
StandardError=append:$INSTALL_DIR/logs/fleet-manager.error.log

# Security settings
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "[7/9] Installing systemd service..."
sudo cp fleet-manager.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fleet-manager.service

echo ""
echo "[8/9] Setting up log rotation..."
sudo tee /etc/logrotate.d/fleet-manager > /dev/null <<EOF
$INSTALL_DIR/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 $USER $USER
}
EOF

echo ""
echo "[9/9] Creating health check script..."
cat > check-health.sh << 'HEALTHEOF'
#!/bin/bash
echo "Fleet Manager Health Check"
echo "======================================"
systemctl is-active --quiet fleet-manager && echo "✓ Service running" || echo "✗ Service NOT running"
systemctl is-enabled --quiet fleet-manager && echo "✓ Auto-start enabled" || echo "✗ Auto-start disabled"
[ -f ~/home-mining-fleet-manager/fleet.db ] && echo "✓ Database exists" || echo "✗ Database missing"
echo ""
echo "Dashboard URL: http://$(hostname -I | awk '{print $1}'):5001"
HEALTHEOF

chmod +x check-health.sh

echo ""
echo "========================================="
echo "Basic Setup Complete!"
echo "========================================="
echo ""
echo "NEXT STEPS:"
echo ""
echo "You now need to copy the application files here:"
echo "  $INSTALL_DIR"
echo ""
echo "Missing files that need to be copied:"
echo "  - app.py (main application)"
echo "  - config.py (configuration)"
echo "  - All files from miners/ directory"
echo "  - All files from database/ directory"
echo "  - All files from static/ directory"
echo "  - All files from templates/ directory"
echo "  - alerts.py, energy.py, thermal.py, weather.py"
echo ""
echo "OPTIONS:"
echo ""
echo "1. Transfer from your computer using USB drive:"
echo "   - Copy the files to a USB drive"
echo "   - Plug into Pi and copy: cp -r /media/usb/files/* $INSTALL_DIR/"
echo ""
echo "2. Download from Git repository (if you have one):"
echo "   - git clone <your-repo> temp"
echo "   - cp -r temp/* $INSTALL_DIR/"
echo ""
echo "3. Use the companion upload script on your Mac"
echo ""
echo "After copying files, start the service:"
echo "  sudo systemctl start fleet-manager"
echo ""
HEALTHEOF

chmod +x "$INSTALL_DIR/pi-direct-install.sh"

echo "Direct installation script created!"
echo ""
echo "Save this script to the Pi and run it there."
