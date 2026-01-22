#!/bin/bash
# Update script to push latest changes from Mac to Raspberry Pi
# Run this on your Mac whenever you make changes

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Load configuration from pi-config.sh
if [ ! -f "pi-config.sh" ]; then
    echo "Error: pi-config.sh not found!"
    echo ""
    echo "Please create pi-config.sh from the template:"
    echo "  cp pi-config.sh.template pi-config.sh"
    echo "  nano pi-config.sh  # Edit with your credentials"
    echo ""
    exit 1
fi

source pi-config.sh

echo "========================================="
echo "Pushing Updates to Raspberry Pi"
echo "========================================="
echo ""

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    echo "Error: sshpass is not installed"
    echo "Install with: brew install hudochenkov/sshpass/sshpass"
    exit 1
fi

echo "[1/4] Checking Pi connectivity..."
if ! ping -c 1 -W 1 $PI_HOST > /dev/null 2>&1; then
    echo "Error: Cannot reach Raspberry Pi at $PI_HOST"
    exit 1
fi
echo "✓ Pi is reachable"

echo ""
echo "[2/4] Transferring files to Raspberry Pi..."
sshpass -p "$PI_PASSWORD" scp -o StrictHostKeyChecking=no -r \
    *.py *.sh *.md *.txt *.service \
    miners/ database/ static/ templates/ tests/ \
    $PI_USER@$PI_HOST:$PI_DIR/

echo "✓ Files transferred"

echo ""
echo "[3/4] Updating dependencies and restarting service..."
sshpass -p "$PI_PASSWORD" ssh -o StrictHostKeyChecking=no $PI_USER@$PI_HOST << 'ENDSSH'
cd ~/home-mining-fleet-manager
source venv/bin/activate
pip install -r requirements.txt --quiet
sudo systemctl restart fleet-manager
sleep 2
ENDSSH

echo "✓ Dependencies updated and service restarted"

echo ""
echo "[4/4] Verifying service status..."
sshpass -p "$PI_PASSWORD" ssh -o StrictHostKeyChecking=no $PI_USER@$PI_HOST \
    "sudo systemctl is-active fleet-manager" > /dev/null && echo "✓ Service is running" || echo "✗ Service failed to start"

echo ""
echo "========================================="
echo "Update Complete!"
echo "========================================="
echo ""
echo "Dashboard: http://$PI_HOST:5001"
echo ""
echo "To view logs:"
echo "  ssh $PI_USER@$PI_HOST"
echo "  sudo journalctl -u fleet-manager -f"
echo ""
