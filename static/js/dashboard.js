/**
 * NoctisCore Dashboard - JavaScript
 * ==================================
 * Scanner Control, Live Updates, Search, Notifications
 */

// ========================= STATE MANAGEMENT =========================

const state = {
    scanning: false,
    currentView: 'home',
    filters: {
        time: '24h',
        scanner: ['bluetooth'],
        device: ['smartphone', 'headset'],
        status: []dashboard
    },
    devices: [],
    notifications: [],
    startTime: null
};
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active class from all
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // Add active class to clicked
            item.classList.add('active');
            
            // Get view name
            const view = item.dataset.view;
            state.currentView = view;
            
            // Update page title
            updatePageTitle(view);
            
            // TODO: Load view content
            console.log('Switched to view:', view);
        });
    });
}

function updatePageTitle(view) {
    const titles = {
        home: 'SCANNER CONTROL',
        scan: 'ACTIVE SCANS',
        stats: 'STATISTICS & ANALYTICS',
        map: 'GPS TRACKING MAP',
        logs: 'SCAN LOGS',
        watch: 'WATCHLIST MANAGEMENT',
        export: 'DATA EXPORT',
        ai: 'AI ANALYSIS'
    };
    
    document.getElementById('page-title').textContent = titles[view] || 'NOCTISCORE';
}

// ========================= SCANNER CONTROL =========================

function initScannerControl() {
    const startBtn = document.getElementById('btn-start-scan');
    const stopBtn = document.getElementById('btn-stop-scan');
    const manualBtn = document.getElementById('manual-scan-btn');
    
    startBtn.addEventListener('click', startScan);
    stopBtn.addEventListener('click', stopScan);
    manualBtn.addEventListener('click', manualScan);
}

async function startScan() {
    console.log('Starting scan...');
    
    try {
        const response = await fetch('/api/scanner/bluetooth/start', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            state.scanning = true;
            state.startTime = Date.now();
            
            // Update UI
            updateScanButtons(true);
            updateScannerStatus('bluetooth', 'active', 'SCANNING');
            
            // Add notification
            addNotification('Scanner Started', 'Bluetooth scan is now running', 'success');
            
            // Start live updates
            startLiveUpdates();
        } else {
            console.error('Failed to start scan:', data.error);
            addNotification('Scan Failed', data.error || 'Could not start scan', 'error');
        }
    } catch (error) {
        console.error('Error starting scan:', error);
        addNotification('Connection Error', 'Could not connect to scanner API', 'error');
    }
}

async function stopScan() {
    console.log('Stopping scan...');
    
    try {
        const response = await fetch('/api/scanner/bluetooth/stop', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            state.scanning = false;
            state.startTime = null;
            
            // Update UI
            updateScanButtons(false);
            updateScannerStatus('bluetooth', 'inactive', 'IDLE');
            
            // Add notification
            addNotification('Scanner Stopped', 'Bluetooth scan has been stopped', 'info');
            
            // Stop live updates
            stopLiveUpdates();
        } else {
            console.error('Failed to stop scan:', data.error);
        }
    } catch (error) {
        console.error('Error stopping scan:', error);
    }
}

async function manualScan() {
    console.log('Performing manual scan...');
    
    addNotification('Manual Scan', 'Starting one-time scan...', 'info');
    
    try {
        const response = await fetch('/api/scanner/bluetooth/manual', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            addNotification('Scan Complete', `Found ${data.device_count || 0} devices`, 'success');
            
            // Refresh device list
            await loadDevices();
        } else {
            addNotification('Scan Failed', data.error || 'Manual scan failed', 'error');
        }
    } catch (error) {
        console.error('Error performing manual scan:', error);
        addNotification('Connection Error', 'Could not perform manual scan', 'error');
    }
}

function updateScanButtons(scanning) {
    const startBtn = document.getElementById('btn-start-scan');
    const stopBtn = document.getElementById('btn-stop-scan');
    
    if (scanning) {
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
}

function updateScannerStatus(scanner, status, text) {
    const led = document.getElementById(`${scanner}-status-led`);
    const statusText = document.getElementById(`${scanner}-status-text`);
    
    if (led) {
        led.className = `status-led ${status}`;
    }
    
    if (statusText) {
        statusText.textContent = text;
    }
}

// ========================= LIVE UPDATES =========================

let updateInterval = null;

function startLiveUpdates() {
    // Update every 2 seconds
    updateInterval = setInterval(async () => {
        await loadDevices();
        await updateScannerCards();
    }, 2000);
}

function stopLiveUpdates() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
}

async function updateScannerCards() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.scanners) {
            // Update Bluetooth
            if (data.scanners.bluetooth) {
                const bt = data.scanners.bluetooth;
                document.getElementById('bt-device-count').textContent = bt.device_count || 0;
                
                if (bt.last_scan) {
                    const time = new Date(bt.last_scan).toLocaleTimeString('de-DE', {
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                    document.getElementById('bt-last-scan').textContent = time;
                }
            }
            
            // Update WiFi
            if (data.scanners.wifi) {
                const wifi = data.scanners.wifi;
                document.getElementById('wifi-device-count').textContent = wifi.device_count || 0;
                
                if (wifi.last_scan) {
                    const time = new Date(wifi.last_scan).toLocaleTimeString('de-DE', {
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                    document.getElementById('wifi-last-scan').textContent = time;
                }
            }
            
            // Update RF
            if (data.scanners.rf) {
                const rf = data.scanners.rf;
                document.getElementById('rf-device-count').textContent = rf.device_count || 0;
                
                if (rf.last_scan) {
                    const time = new Date(rf.last_scan).toLocaleTimeString('de-DE', {
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                    document.getElementById('rf-last-scan').textContent = time;
                }
            }
        }
    } catch (error) {
        console.error('Error updating scanner cards:', error);
    }
}

async function loadDevices() {
    try {
        const response = await fetch('/api/devices');
        const devices = await response.json();
        
        state.devices = devices;
        updateDeviceTable(devices);
        updateSystemInfo(devices);
    } catch (error) {
        console.error('Error loading devices:', error);
    }
}

function updateDeviceTable(devices) {
    const tbody = document.getElementById('device-table');
    
    if (!devices || devices.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No devices detected yet. Start a scan to begin.</td></tr>';
        return;
    }
    
    tbody.innerHTML = devices.slice(0, 50).map(device => {
        const time = device.timestamp ? new Date(device.timestamp).toLocaleTimeString('de-DE') : '--:--';
        const mac = device.mac || 'Unknown';
        const name = device.name || 'Unknown Device';
        const type = device.type || 'Unknown';
        const rssi = device.rssi || '--';
        const status = device.status || 'offline';
        
        return `
            <tr>
                <td>${time}</td>
                <td style="color: var(--accent-cyan);">${mac}</td>
                <td>${name}</td>
                <td>${type}</td>
                <td>${rssi}</td>
                <td>
                    <div class="status-indicator ${status === 'online' ? '' : 'inactive'}"></div>
                </td>
            </tr>
        `;
    }).join('');
}

function updateSystemInfo(devices) {
    document.getElementById('system-device-count').textContent = devices.length;
}

// ========================= STATUS POLLING =========================

async function pollStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.status === 'online') {
            document.getElementById('system-status').textContent = 'OPERATIONAL';
            document.getElementById('system-status').className = 'text-green';
        } else {
            document.getElementById('system-status').textContent = 'ERROR';
            document.getElementById('system-status').className = 'text-red';
        }
        
        // Check if bluetooth scanner is running
        if (data.scanners && data.scanners.bluetooth && data.scanners.bluetooth.running) {
            if (!state.scanning) {
                state.scanning = true;
                updateScanButtons(true);
                updateScannerStatus('bluetooth', 'active', 'SCANNING');
                startLiveUpdates();
            }
        }
    } catch (error) {
        console.error('Status poll error:', error);
        document.getElementById('system-status').textContent = 'DISCONNECTED';
        document.getElementById('system-status').className = 'text-red';
    }
    
    // Poll every 5 seconds
    setTimeout(pollStatus, 5000);
}

function updateUptime() {
    if (state.startTime) {
        const elapsed = Date.now() - state.startTime;
        const hours = Math.floor(elapsed / 3600000);
        const minutes = Math.floor((elapsed % 3600000) / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);
        
        document.getElementById('system-uptime').textContent = 
            `${hours}h ${minutes}m ${seconds}s`;
    } else {
        document.getElementById('system-uptime').textContent = '--:--';
    }
}

// ========================= SEARCH =========================

function initSearch() {
    const searchInput = document.getElementById('search-input');
    const searchDropdown = document.getElementById('search-dropdown');
    
    let searchTimeout = null;
    
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        
        // Clear previous timeout
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        
        if (query.length < 2) {
            searchDropdown.classList.remove('show');
            return;
        }
        
        // Debounce search
        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 300);
    });
    
    searchInput.addEventListener('focus', () => {
        if (searchInput.value.trim().length >= 2) {
            searchDropdown.classList.add('show');
        }
    });
    
    // Close on click outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
            searchDropdown.classList.remove('show');
        }
    });
}

async function performSearch(query) {
    const searchDropdown = document.getElementById('search-dropdown');
    
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        
        if (results.length === 0) {
            searchDropdown.innerHTML = '<div class="search-no-results">No results found</div>';
        } else {
            searchDropdown.innerHTML = results.map(result => `
                <div class="search-result">
                    <div class="search-result-title">${result.mac || 'Unknown'}</div>
                    <div class="search-result-subtitle">${result.name || 'Unknown Device'} - ${result.timestamp || ''}</div>
                </div>
            `).join('');
        }
        
        searchDropdown.classList.add('show');
    } catch (error) {
        console.error('Search error:', error);
        searchDropdown.innerHTML = '<div class="search-no-results">Search failed</div>';
        searchDropdown.classList.add('show');
    }
}

// ========================= NOTIFICATIONS =========================

function initNotifications() {
    const bell = document.getElementById('notification-bell');
    const dropdown = document.getElementById('notification-dropdown');
    
    bell.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('show');
    });
    
    // Close on click outside
    document.addEventListener('click', (e) => {
        if (!bell.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });
}

function addNotification(title, message, type = 'info') {
    const notification = {
        id: Date.now(),
        title,
        message,
        type,
        time: new Date(),
        unread: true
    };
    
    state.notifications.unshift(notification);
    
    // Keep only last 20
    if (state.notifications.length > 20) {
        state.notifications = state.notifications.slice(0, 20);
    }
    
    updateNotificationUI();
}

function updateNotificationUI() {
    const badge = document.getElementById('notification-badge');
    const list = document.getElementById('notification-list');
    
    // Update badge
    const unreadCount = state.notifications.filter(n => n.unread).length;
    badge.textContent = unreadCount;
    badge.style.display = unreadCount > 0 ? 'flex' : 'none';
    
    // Update list
    if (state.notifications.length === 0) {
        list.innerHTML = '<div class="notification-item" style="text-align: center; color: var(--text-muted);">No notifications</div>';
    } else {
        list.innerHTML = state.notifications.map(notif => {
            const timeStr = formatTimeAgo(notif.time);
            return `
                <div class="notification-item ${notif.unread ? 'unread' : ''}">
                    <div class="notification-title">${notif.title}</div>
                    <div class="notification-message">${notif.message}</div>
                    <div class="notification-time">${timeStr}</div>
                </div>
            `;
        }).join('');
    }
}

function clearNotifications() {
    state.notifications = [];
    updateNotificationUI();
    document.getElementById('notification-dropdown').classList.remove('show');
}

function formatTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
}

// ========================= FILTERS =========================

function initFilters() {
    const filterItems = document.querySelectorAll('.sidebar-item[data-filter]');
    
    filterItems.forEach(item => {
        item.addEventListener('click', () => {
            const checkbox = item.querySelector('.filter-checkbox');
            const filterType = item.dataset.filter;
            const filterValue = item.dataset.value;
            
            if (!checkbox || !filterType || !filterValue) return;
            
            // Toggle checkbox
            const isChecked = checkbox.classList.contains('checked');
            
            if (filterType === 'time') {
                // Only one time filter at a time
                document.querySelectorAll('[data-filter="time"] .filter-checkbox').forEach(cb => {
                    cb.classList.remove('checked');
                    cb.textContent = '';
                });
                checkbox.classList.add('checked');
                checkbox.textContent = '✓';
                state.filters.time = filterValue;
            } else {
                // Multiple selections allowed
                if (isChecked) {
                    checkbox.classList.remove('checked');
                    checkbox.textContent = '';
                    
                    // Remove from array
                    const index = state.filters[filterType].indexOf(filterValue);
                    if (index > -1) {
                        state.filters[filterType].splice(index, 1);
                    }
                } else {
                    checkbox.classList.add('checked');
                    checkbox.textContent = '✓';
                    
                    // Add to array
                    if (!state.filters[filterType].includes(filterValue)) {
                        state.filters[filterType].push(filterValue);
                    }
                }
            }
            
            console.log('Filters updated:', state.filters);
            
            // TODO: Apply filters to device list
            loadDevices();
        });
    });
}

// ========================= UTILITY FUNCTIONS =========================

function showToast(message, type = 'info') {
    // TODO: Implement toast notifications
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// Expose some functions globally for onclick handlers
window.clearNotifications = clearNotifications;
