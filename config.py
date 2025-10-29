"""
Configuration for Home Mining Fleet Manager
"""
import os

# Network settings
NETWORK_SUBNET = "10.0.0.0/24"
DISCOVERY_TIMEOUT = 2  # seconds per IP
DISCOVERY_THREADS = 20  # parallel scan threads

# Monitoring settings
UPDATE_INTERVAL = 15  # seconds between status updates
STATUS_TIMEOUT = 3  # seconds per miner status check

# Database
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "fleet.db")

# Flask settings
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
DEBUG = True

# Miner API settings
BITAXE_API_TIMEOUT = 2
CGMINER_API_TIMEOUT = 2
CGMINER_PORT = 4028

# Supported miner types
MINER_TYPES = {
    "BITAXE": "Bitaxe",
    "ANTMINER": "Antminer",
    "WHATSMINER": "Whatsminer",
    "AVALON": "Avalon",
    "UNKNOWN": "Unknown"
}
