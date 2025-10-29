"""
Home Mining Fleet Manager - Main Application
"""
import logging
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Thread, Lock
from datetime import datetime
from typing import List, Dict
from flask import Flask, jsonify, render_template, request

import config
from database import Database
from miners import MinerDetector, Miner

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)


class FleetManager:
    """Manages the mining fleet"""

    def __init__(self):
        self.db = Database(config.DATABASE_PATH)
        self.detector = MinerDetector()
        self.miners: Dict[str, Miner] = {}  # ip -> Miner
        self.lock = Lock()
        self.monitoring_thread = None
        self.monitoring_active = False

        # Load miners from database
        self._load_miners_from_db()

    def _load_miners_from_db(self):
        """Load known miners from database"""
        logger.info("Loading miners from database...")
        miners_data = self.db.get_all_miners()
        for miner_data in miners_data:
            ip = miner_data['ip']
            # Try to recreate Miner instance
            miner = self.detector.detect(ip)
            if miner:
                with self.lock:
                    self.miners[ip] = miner
                logger.info(f"Loaded miner {ip} ({miner.type})")

    def discover_miners(self, subnet: str = None) -> List[Miner]:
        """
        Discover miners on network using parallel scanning

        Args:
            subnet: Network subnet (e.g., "10.0.0.0/24")

        Returns:
            List of newly discovered miners
        """
        if subnet is None:
            subnet = config.NETWORK_SUBNET

        logger.info(f"Starting network discovery on {subnet}")
        network = ipaddress.IPv4Network(subnet, strict=False)

        discovered = []

        def check_ip(ip_str: str) -> Miner:
            """Check single IP for miner"""
            miner = self.detector.detect(ip_str)
            if miner:
                logger.info(f"Found miner at {ip_str}")
            return miner

        # Parallel scan
        with ThreadPoolExecutor(max_workers=config.DISCOVERY_THREADS) as executor:
            futures = {
                executor.submit(check_ip, str(ip)): str(ip)
                for ip in network.hosts()
            }

            for future in as_completed(futures):
                try:
                    miner = future.result()
                    if miner:
                        with self.lock:
                            self.miners[miner.ip] = miner
                            # Save to database
                            self.db.update_miner(
                                miner.ip,
                                miner.type,
                                miner.model
                            )
                        discovered.append(miner)
                except Exception as e:
                    logger.error(f"Error checking IP: {e}")

        logger.info(f"Discovery complete. Found {len(discovered)} miners")
        return discovered

    def update_all_miners(self):
        """Update status of all miners in parallel"""
        if not self.miners:
            return

        def update_miner(miner: Miner):
            """Update single miner status"""
            try:
                status = miner.update_status()
                if status.get('status') == 'online':
                    # Save stats to database
                    miner_data = self.db.get_miner_by_ip(miner.ip)
                    if miner_data:
                        self.db.add_stats(
                            miner_data['id'],
                            hashrate=status.get('hashrate'),
                            temperature=status.get('temperature'),
                            power=status.get('power'),
                            fan_speed=status.get('fan_speed'),
                            status='online'
                        )
            except Exception as e:
                logger.error(f"Error updating miner {miner.ip}: {e}")

        # Update all miners in parallel
        with ThreadPoolExecutor(max_workers=len(self.miners)) as executor:
            futures = [
                executor.submit(update_miner, miner)
                for miner in self.miners.values()
            ]
            # Wait for all to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error in update: {e}")

    def start_monitoring(self):
        """Start background monitoring thread"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return

        self.monitoring_active = True

        def monitor_loop():
            logger.info("Monitoring thread started")
            while self.monitoring_active:
                try:
                    self.update_all_miners()
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")

                # Sleep in small chunks to allow quick shutdown
                for _ in range(config.UPDATE_INTERVAL):
                    if not self.monitoring_active:
                        break
                    import time
                    time.sleep(1)

            logger.info("Monitoring thread stopped")

        self.monitoring_thread = Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Monitoring stopped")

    def get_fleet_stats(self) -> Dict:
        """Get aggregated fleet statistics"""
        with self.lock:
            online_count = 0
            total_hashrate = 0
            total_power = 0
            avg_temp = 0
            temp_count = 0

            for miner in self.miners.values():
                if miner.last_status and miner.last_status.get('status') == 'online':
                    online_count += 1
                    total_hashrate += miner.last_status.get('hashrate', 0)
                    total_power += miner.last_status.get('power', 0)
                    if miner.last_status.get('temperature'):
                        avg_temp += miner.last_status['temperature']
                        temp_count += 1

            return {
                'total_miners': len(self.miners),
                'online_miners': online_count,
                'offline_miners': len(self.miners) - online_count,
                'total_hashrate': total_hashrate,
                'total_power': total_power,
                'avg_temperature': avg_temp / temp_count if temp_count > 0 else 0,
                'last_update': datetime.now().isoformat()
            }

    def get_all_miners_status(self) -> List[Dict]:
        """Get status of all miners"""
        with self.lock:
            return [miner.to_dict() for miner in self.miners.values()]


# Global fleet manager
fleet = FleetManager()


# Flask Routes

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')


@app.route('/api/miners', methods=['GET'])
def get_miners():
    """Get all miners and their status"""
    miners = fleet.get_all_miners_status()
    return jsonify({
        'success': True,
        'miners': miners
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get fleet statistics"""
    stats = fleet.get_fleet_stats()
    return jsonify({
        'success': True,
        'stats': stats
    })


@app.route('/api/discover', methods=['POST'])
def discover():
    """Trigger network discovery"""
    data = request.get_json() or {}
    subnet = data.get('subnet', config.NETWORK_SUBNET)

    try:
        discovered = fleet.discover_miners(subnet)
        return jsonify({
            'success': True,
            'discovered': len(discovered),
            'message': f'Discovered {len(discovered)} miners'
        })
    except Exception as e:
        logger.error(f"Discovery error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/miner/<ip>/restart', methods=['POST'])
def restart_miner(ip: str):
    """Restart specific miner"""
    with fleet.lock:
        miner = fleet.miners.get(ip)
        if not miner:
            return jsonify({
                'success': False,
                'error': 'Miner not found'
            }), 404

        success = miner.restart()
        return jsonify({
            'success': success,
            'message': 'Restart command sent' if success else 'Restart failed'
        })


@app.route('/api/miner/<ip>', methods=['DELETE'])
def delete_miner(ip: str):
    """Remove miner from fleet"""
    with fleet.lock:
        if ip in fleet.miners:
            del fleet.miners[ip]
            fleet.db.delete_miner(ip)
            return jsonify({
                'success': True,
                'message': f'Miner {ip} removed'
            })
        return jsonify({
            'success': False,
            'error': 'Miner not found'
        }), 404


if __name__ == '__main__':
    logger.info("Starting Home Mining Fleet Manager")

    # Start monitoring
    fleet.start_monitoring()

    try:
        app.run(
            host=config.FLASK_HOST,
            port=config.FLASK_PORT,
            debug=config.DEBUG
        )
    finally:
        fleet.stop_monitoring()
