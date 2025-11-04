"""
Miner detection and management
"""
import logging
from typing import Optional, Dict
from .base import MinerAPIHandler
from .bitaxe import BitaxeAPIHandler
from .cgminer import CGMinerAPIHandler
import config

logger = logging.getLogger(__name__)


class Miner:
    """Represents a single miner with its API handler"""

    def __init__(self, ip: str, miner_type: str, api_handler: MinerAPIHandler, custom_name: str = None):
        self.ip = ip
        self.type = miner_type
        self.api_handler = api_handler
        self.last_status = None
        self.model = None
        self.custom_name = custom_name

    def update_status(self) -> Dict:
        """Update and return current status"""
        self.last_status = self.api_handler.get_status(self.ip)
        if 'model' in self.last_status:
            self.model = self.last_status['model']
        return self.last_status

    def apply_settings(self, settings: Dict) -> bool:
        """Apply settings to this miner"""
        return self.api_handler.apply_settings(self.ip, settings)

    def restart(self) -> bool:
        """Restart this miner"""
        return self.api_handler.restart(self.ip)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'ip': self.ip,
            'type': self.type,
            'model': self.model,
            'custom_name': self.custom_name,
            'last_status': self.last_status
        }


class MinerDetector:
    """Factory for detecting and creating Miner instances"""

    def __init__(self):
        # Order matters - try Bitaxe first (fastest API)
        self.handlers = [
            (config.MINER_TYPES['BITAXE'], BitaxeAPIHandler()),
            (config.MINER_TYPES['ANTMINER'], CGMinerAPIHandler()),
        ]

    def detect(self, ip: str) -> Optional[Miner]:
        """
        Detect miner type at given IP and return Miner instance

        Args:
            ip: IP address to probe

        Returns:
            Miner instance if detected, None otherwise
        """
        logger.debug(f"Detecting miner at {ip}")

        for miner_type, handler in self.handlers:
            try:
                if handler.detect(ip):
                    logger.info(f"Detected {miner_type} at {ip}")
                    miner = Miner(ip, miner_type, handler)
                    # Get initial status to populate model
                    miner.update_status()
                    return miner
            except Exception as e:
                logger.debug(f"Detection error for {miner_type} at {ip}: {e}")
                continue

        logger.debug(f"No miner detected at {ip}")
        return None

    def scan_network(self, subnet: str = "10.0.0.0/24") -> list:
        """
        Scan network for miners (stub - use parallel scanner in main app)

        Args:
            subnet: Network subnet to scan

        Returns:
            List of Miner instances
        """
        # This is a placeholder - actual parallel scanning
        # should be done in the main application using ThreadPoolExecutor
        logger.warning("Use FleetManager.discover_miners() for network scanning")
        return []
