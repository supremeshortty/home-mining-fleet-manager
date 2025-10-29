// Mining Fleet Manager Dashboard
const API_BASE = '';
const UPDATE_INTERVAL = 5000; // 5 seconds

let updateTimer = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    startAutoRefresh();

    // Discovery button
    document.getElementById('discover-btn').addEventListener('click', discoverMiners);
});

// Load all dashboard data
async function loadDashboard() {
    try {
        await Promise.all([
            loadStats(),
            loadMiners()
        ]);
        updateLastUpdateTime();
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showAlert('Error loading dashboard data', 'error');
    }
}

// Load fleet statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const data = await response.json();

        if (data.success) {
            const stats = data.stats;
            document.getElementById('total-miners').textContent = stats.total_miners;
            document.getElementById('online-miners').textContent = stats.online_miners;
            document.getElementById('offline-miners').textContent = stats.offline_miners;
            document.getElementById('total-hashrate').textContent = formatHashrate(stats.total_hashrate);
            document.getElementById('total-power').textContent = `${stats.total_power.toFixed(1)} W`;
            document.getElementById('avg-temp').textContent = `${stats.avg_temperature.toFixed(1)}°C`;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load miners list
async function loadMiners() {
    try {
        const response = await fetch(`${API_BASE}/api/miners`);
        const data = await response.json();

        if (data.success) {
            displayMiners(data.miners);
        }
    } catch (error) {
        console.error('Error loading miners:', error);
    }
}

// Display miners in grid
function displayMiners(miners) {
    const container = document.getElementById('miners-container');

    if (miners.length === 0) {
        container.innerHTML = '<p class="no-miners">No miners found. Click "Discover Miners" to scan your network.</p>';
        return;
    }

    const minersHTML = miners.map(miner => createMinerCard(miner)).join('');
    container.innerHTML = `<div class="miners-grid">${minersHTML}</div>`;

    // Attach event listeners for actions
    miners.forEach(miner => {
        const deleteBtn = document.getElementById(`delete-${miner.ip}`);
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => deleteMiner(miner.ip));
        }

        const restartBtn = document.getElementById(`restart-${miner.ip}`);
        if (restartBtn) {
            restartBtn.addEventListener('click', () => restartMiner(miner.ip));
        }
    });
}

// Create HTML for single miner card
function createMinerCard(miner) {
    const status = miner.last_status || {};
    const isOnline = status.status === 'online';
    const offlineClass = isOnline ? '' : 'offline';

    return `
        <div class="miner-card ${offlineClass}">
            <div class="miner-header">
                <div class="miner-title">${miner.model || miner.type}</div>
                <div class="miner-type">${miner.type}</div>
            </div>
            <div class="miner-ip">${miner.ip}</div>

            ${isOnline ? `
                <div class="miner-stats">
                    <div class="miner-stat">
                        <span class="miner-stat-label">Hashrate</span>
                        <span class="miner-stat-value">${formatHashrate(status.hashrate)}</span>
                    </div>
                    <div class="miner-stat">
                        <span class="miner-stat-label">Temperature</span>
                        <span class="miner-stat-value">${status.temperature?.toFixed(1) || 'N/A'}°C</span>
                    </div>
                    <div class="miner-stat">
                        <span class="miner-stat-label">Power</span>
                        <span class="miner-stat-value">${status.power?.toFixed(1) || 'N/A'} W</span>
                    </div>
                    <div class="miner-stat">
                        <span class="miner-stat-label">Fan Speed</span>
                        <span class="miner-stat-value">${status.fan_speed || 'N/A'}</span>
                    </div>
                </div>
            ` : `
                <div class="status-offline" style="text-align: center; padding: 20px;">
                    ⚠️ Offline
                </div>
            `}

            <div class="miner-actions">
                <button id="restart-${miner.ip}" class="btn btn-primary" ${!isOnline ? 'disabled' : ''}>
                    Restart
                </button>
                <button id="delete-${miner.ip}" class="btn btn-danger">
                    Remove
                </button>
            </div>
        </div>
    `;
}

// Format hashrate to human-readable
function formatHashrate(hashrate) {
    if (!hashrate) return '0 H/s';

    const units = ['H/s', 'KH/s', 'MH/s', 'GH/s', 'TH/s', 'PH/s'];
    let value = hashrate;
    let unitIndex = 0;

    while (value >= 1000 && unitIndex < units.length - 1) {
        value /= 1000;
        unitIndex++;
    }

    return `${value.toFixed(2)} ${units[unitIndex]}`;
}

// Discover miners
async function discoverMiners() {
    const btn = document.getElementById('discover-btn');
    btn.disabled = true;
    btn.textContent = 'Discovering...';

    showAlert('Scanning network for miners... This may take up to 60 seconds.', 'success');

    try {
        const response = await fetch(`${API_BASE}/api/discover`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.success) {
            showAlert(`Discovery complete! Found ${data.discovered} new miners.`, 'success');
            loadDashboard();
        } else {
            showAlert(`Discovery failed: ${data.error}`, 'error');
        }
    } catch (error) {
        showAlert(`Discovery error: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Discover Miners';
    }
}

// Restart miner
async function restartMiner(ip) {
    if (!confirm(`Restart miner at ${ip}?`)) return;

    try {
        const response = await fetch(`${API_BASE}/api/miner/${ip}/restart`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showAlert(`Restart command sent to ${ip}`, 'success');
        } else {
            showAlert(`Failed to restart ${ip}: ${data.error}`, 'error');
        }
    } catch (error) {
        showAlert(`Error restarting ${ip}: ${error.message}`, 'error');
    }
}

// Delete miner
async function deleteMiner(ip) {
    if (!confirm(`Remove miner ${ip} from fleet?`)) return;

    try {
        const response = await fetch(`${API_BASE}/api/miner/${ip}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showAlert(`Miner ${ip} removed`, 'success');
            loadDashboard();
        } else {
            showAlert(`Failed to remove ${ip}: ${data.error}`, 'error');
        }
    } catch (error) {
        showAlert(`Error removing ${ip}: ${error.message}`, 'error');
    }
}

// Show alert message
function showAlert(message, type) {
    const alert = document.getElementById('discovery-status');
    alert.textContent = message;
    alert.className = `alert ${type}`;
    alert.style.display = 'block';

    setTimeout(() => {
        alert.style.display = 'none';
    }, 5000);
}

// Auto-refresh
function startAutoRefresh() {
    updateTimer = setInterval(loadDashboard, UPDATE_INTERVAL);
}

function updateLastUpdateTime() {
    const now = new Date().toLocaleTimeString();
    document.getElementById('last-update').textContent = `Last update: ${now}`;
}
