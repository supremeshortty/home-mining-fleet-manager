"""
Bitaxe ESP32 API Handler
"""
import requests
import logging
from typing import Dict
from .base import MinerAPIHandler
import config

logger = logging.getLogger(__name__)


class BitaxeAPIHandler(MinerAPIHandler):
    """Handler for Bitaxe miners using ESP32 API"""

    def __init__(self):
        self.timeout = config.BITAXE_API_TIMEOUT

    def detect(self, ip: str) -> bool:
        """Check if this is a Bitaxe miner"""
        try:
            response = requests.get(
                f"http://{ip}/api/system/info",
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                # Bitaxe has specific fields like ASICModel
                if 'ASICModel' in data or 'power' in data:
                    return True
        except Exception as e:
            logger.debug(f"Bitaxe detection failed for {ip}: {e}")
        return False

    def get_status(self, ip: str) -> Dict:
        """Get status from Bitaxe API"""
        try:
            response = requests.get(
                f"http://{ip}/api/system/info",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            # Parse Bitaxe response format
            return {
                'hashrate': float(data.get('hashRate', 0)),
                'temperature': float(data.get('temp', 0)),
                'power': float(data.get('power', 0)),
                'fan_speed': int(data.get('fanspeed', 0)),
                'model': data.get('ASICModel', 'Bitaxe'),
                'frequency': data.get('frequency', 0),
                'status': 'online',
                'raw': data
            }

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout getting status from Bitaxe at {ip}")
            return {'status': 'offline', 'error': 'timeout'}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting status from Bitaxe at {ip}: {e}")
            return {'status': 'error', 'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error with Bitaxe at {ip}: {e}")
            return {'status': 'error', 'error': str(e)}

    def apply_settings(self, ip: str, settings: Dict) -> bool:
        """Apply settings to Bitaxe"""
        try:
            response = requests.patch(
                f"http://{ip}/api/system",
                json=settings,
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"Applied settings to Bitaxe at {ip}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply settings to Bitaxe at {ip}: {e}")
            return False

    def restart(self, ip: str) -> bool:
        """Restart Bitaxe"""
        try:
            response = requests.post(
                f"http://{ip}/api/system/restart",
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"Restart command sent to Bitaxe at {ip}")
            return True
        except Exception as e:
            logger.error(f"Failed to restart Bitaxe at {ip}: {e}")
            return False
