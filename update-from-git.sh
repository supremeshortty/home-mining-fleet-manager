#!/bin/bash
# Update script for Raspberry Pi - pulls latest from Git
# Run this ON the Raspberry Pi to update from GitHub

set -e

INSTALL_DIR="$HOME/home-mining-fleet-manager"

echo "========================================="
echo "Updating Fleet Manager from Git"
echo "========================================="
echo ""

cd "$INSTALL_DIR"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Git repository not initialized. Setting up..."
    read -p "Enter your GitHub repository URL (e.g., https://github.com/username/dirtysats.git): " REPO_URL

    if [ -z "$REPO_URL" ]; then
        echo "Error: Repository URL is required"
        exit 1
    fi

    git init
    git remote add origin "$REPO_URL"
    echo "✓ Git initialized"
fi

echo "[1/5] Fetching latest changes from GitHub..."
git fetch origin

echo ""
echo "[2/5] Pulling latest code..."
git pull origin main || git pull origin master

echo ""
echo "[3/5] Updating dependencies..."
source venv/bin/activate
pip install -r requirements.txt --quiet

echo ""
echo "[4/5] Restarting service..."
sudo systemctl restart fleet-manager
sleep 2

echo ""
echo "[5/5] Verifying service..."
if sudo systemctl is-active --quiet fleet-manager; then
    echo "✓ Service is running"
else
    echo "✗ Service failed to start"
    echo "Check logs with: sudo journalctl -u fleet-manager -n 50"
    exit 1
fi

echo ""
echo "========================================="
echo "Update Complete!"
echo "========================================="
echo ""
echo "Dashboard: http://$(hostname -I | awk '{print $1}'):5001"
echo ""
