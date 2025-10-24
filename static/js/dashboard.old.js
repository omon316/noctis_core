// NoctisCore Dashboard JavaScript
// ==================================

// State
let notifications = [];
let currentFilters = {
    time: ['1h'],
    scanner: ['bluetooth'],
    device: ['smartphone', 'headset'],
    status: []
};

// ========================= INITIALIZATION =========================

document.addEventListener('DOMContentLoaded', () => {
    console.log('NoctisCore Dashboard loaded');
    
    // Initialize event listeners
    initNavigation();
    initFilters();
    initSearch();
    initNotifications();
    
    // Load initial data
    loadStatus();
    loadLogs();
});

// ========================= NAVIGATION =========================

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const view = item.dataset.view;
            switchView(view);
            
            // Update active state
            navItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        });
    });
}

function switchView(viewName) {
    const views = document.querySelectorAll('.content-view');
    views.forEach(view => {
        view.classList.remove('active');
    });
    
    const targetView = document.getElementById(`view-${viewName}`);
    if (targetView) {
        targetView.classList.add('active');
    }
    
    console.log(`Switched to view: ${viewName}`);
}

// ========================= FILTERS =========================

function initFilters() {
    const filterItems = document.querySelectorAll('.sidebar-item[data-filter]');
    
    filterItems.forEach(item => {
        item.addEventListener('click', () => {
            const filterType = item.dataset.filter;
            const filterValue = item.dataset.value;
            const checkbox = item.querySelector('.filter-checkbox');
            
            // Toggle checkbox
            if (checkbox.classList.contains('checked')) {
                checkbox.classList.remove('checked');
                checkbox.textContent = '';
                removeFilter(filterType, filterValue);
            } else {
                checkbox.classList.add('checked');
                checkbox.textContent = '✓';
                addFilter(filterType, filterValue);
            }
            
            // Apply filters
            applyFilters();
        });
    });
}

function addFilter(type, value) {
    if (!currentFilters[type].includes(value)) {
        currentFilters[type].push(value);
    }
}

function removeFilter(type, value) {
    currentFilters[type] = currentFilters[type].filter(v => v !== value);
}

function applyFilters() {
    console.log('Applying filters:', currentFilters);
    // Reload data with filters
    loadLogs();
}

// ========================= SEARCH =========================

function initSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchDropdown = document.getElementById('searchDropdown');
    
    let searchTimeout;
    
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value;
        
        clearTimeout(searchTimeout);
        
        if (query.length > 0) {
            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, 300);
        } else {
            searchDropdown.classList.remove('show');
        }
    });
    
    searchInput.addEventListener('focus', () => {
        if (searchInput.value.length > 0) {
            searchDropdown.classList.add('show');
        }
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-container')) {
            searchDropdown.classList.remove('show');
        }
    });
}

async function performSearch(query) {
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        
        displaySearchResults(results);
    } catch (error) {
        console.error('Search error:', error);
    }
}

function displaySearchResults(results) {
    const dropdown = document.getElementById('searchDropdown');
    
    if (results.length === 0) {
        dropdown.innerHTML = '<div class="search-result" style="color: #666;">NO RESULTS FOUND</div>';
    } else {
        dropdown.innerHTML = results.map(result => `
            <div class="search-result">
                <div class="search-result-title">${result.mac}</div>
                <div class="search-result-subtitle">${result.name} // ${result.timestamp}</div>
            </div>
        `).join('');
    }
    
    dropdown.classList.add('show');
}

// ========================= NOTIFICATIONS =========================

function initNotifications() {
    const bell = document.getElementById('notificationBell');
    const dropdown = document.getElementById('notificationDropdown');
    
    bell.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('show');
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.notification-container')) {
            dropdown.classList.remove('show');
        }
    });
}

function addNotification(title, message) {
    const notification = {
        title,
        message,
        time: new Date().toISOString(),
        unread: true
    };
    
    notifications.unshift(notification);
    updateNotificationDisplay();
}

function updateNotificationDisplay() {
    const badge = document.getElementById('notificationBadge');
    const list = document.getElementById('notificationList');
    
    // Update badge
    const unreadCount = notifications.filter(n => n.unread).length;
    badge.textContent = unreadCount;
    badge.style.display = unreadCount > 0 ? 'flex' : 'none';
    
    // Update list
    if (notifications.length === 0) {
        list.innerHTML = '<div style="padding: 1rem; text-align: center; color: #666;">NO NOTIFICATIONS</div>';
    } else {
        list.innerHTML = notifications.map(notif => `
            <div class="notification-item ${notif.unread ? 'unread' : ''}">
                <div class="notification-title">${notif.title}</div>
                <div class="notification-message">${notif.message}</div>
                <div class="notification-time">${formatTimestamp(notif.time)}</div>
            </div>
        `).join('');
    }
}

function formatTimestamp(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000); // seconds
    
    if (diff < 60) return `${diff}S AGO`;
    if (diff < 3600) return `${Math.floor(diff / 60)}M AGO`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}H AGO`;
    return `${Math.floor(diff / 86400)}D AGO`;
}

// ========================= DATA LOADING =========================

async function loadStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        updateDashboard(data);
    } catch (error) {
        console.error('Error loading status:', error);
    }
}

async function loadLogs() {
    try {
        const response = await fetch('/api/logs?limit=100');
        const logs = await response.json();
        
        updateActivityTable(logs);
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

function updateDashboard(data) {
    // Update scanner cards
    Object.entries(data.scanners).forEach(([scanner, state]) => {
        const countEl = document.getElementById(`${scanner}-count`);
        const statusEl = document.getElementById(`${scanner}-status`);
        
        if (countEl) countEl.textContent = state.device_count;
        if (statusEl) {
            statusEl.textContent = state.running ? 'ONLINE' : 'OFFLINE';
            statusEl.style.color = state.running ? '#5fbf8a' : '#666666';
        }
    });
}

function updateActivityTable(logs) {
    const tbody = document.getElementById('activity-body');
    
    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #666;">NO RECENT ACTIVITY</td></tr>';
        return;
    }
    
    tbody.innerHTML = logs.slice(0, 10).map(log => `
        <tr>
            <td>${log.timestamp}</td>
            <td style="color: #6b9bd1; font-weight: 700;">${log.mac}</td>
            <td>${log.name}</td>
            <td>${log.scanner.toUpperCase()}</td>
            <td style="color: #5fbf8a;">ONLINE</td>
        </tr>
    `).join('');
}

// ========================= SCANNER CONTROL =========================

async function startScanner(scannerType) {
    try {
        const response = await fetch(`/api/scanner/${scannerType}/start`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            addNotification('SCANNER STARTED', `${scannerType.toUpperCase()} scanner is now active`);
            updateScannerStatus(scannerType, true);
        }
    } catch (error) {
        console.error('Error starting scanner:', error);
        addNotification('ERROR', `Failed to start ${scannerType} scanner`);
    }
}

async function stopScanner(scannerType) {
    try {
        const response = await fetch(`/api/scanner/${scannerType}/stop`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            addNotification('SCANNER STOPPED', `${scannerType.toUpperCase()} scanner is now inactive`);
            updateScannerStatus(scannerType, false);
        }
    } catch (error) {
        console.error('Error stopping scanner:', error);
        addNotification('ERROR', `Failed to stop ${scannerType} scanner`);
    }
}

function updateScannerStatus(scanner, running) {
    const statusEl = document.getElementById(`${scanner}-scanner-status`);
    if (statusEl) {
        statusEl.textContent = running ? '● SCANNING' : '● IDLE';
        statusEl.style.color = running ? '#5fbf8a' : '#666666';
    }
}

// ========================= UTILITY =========================

// Current stats filter
let currentStatsFilter = 'all';

// Auto-refresh status every 5 seconds
setInterval(() => {
    loadStatus();
    
    // Refresh stats if on stats view
    const statsView = document.getElementById('view-stats');
    if (statsView && statsView.classList.contains('active')) {
        loadStatsData();
    }
}, 5000);

// Update notification times every 10 seconds
setInterval(() => {
    updateNotificationDisplay();
}, 10000);

// ========================= STATS FUNCTIONS =========================

function setStatsFilter(filter) {
    currentStatsFilter = filter;
    
    // Update active button
    document.querySelectorAll('.time-filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
    
    // Reload stats
    loadStatsData();
}

async function loadStatsData() {
    try {
        // Load overview
        const overviewResponse = await fetch('/api/stats/overview');
        const overview = await overviewResponse.json();
        
        document.getElementById('stat-total').textContent = overview.total_scans;
        document.getElementById('stat-unique').textContent = overview.unique_devices;
        document.getElementById('stat-24h').textContent = overview.last_24h;
        document.getElementById('stat-1h').textContent = overview.last_hour;
        
        // Load top devices
        const filterParam = currentStatsFilter === 'all' ? '' : `?filter=${currentStatsFilter}`;
        const topResponse = await fetch(`/api/stats/top-devices${filterParam}`);
        const topData = await topResponse.json();
        
        updateTopDevicesTable(topData.devices);
        
        // Load hourly activity
        const hourlyResponse = await fetch(`/api/stats/hourly${filterParam}`);
        const hourlyData = await hourlyResponse.json();
        
        updateHourlyChart(hourlyData);
        
        // Load advanced stats
        const advancedResponse = await fetch(`/api/stats/advanced${filterParam}`);
        const advancedData = await advancedResponse.json();
        
        document.getElementById('stat-timespan').textContent = advancedData.timespan_days;
        document.getElementById('stat-avg').textContent = advancedData.avg_scans_per_device;
        document.getElementById('stat-median').textContent = advancedData.median_scans;
        document.getElementById('stat-growth').textContent = advancedData.growth_rate_24h + '%';
        
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function updateTopDevicesTable(devices) {
    const tbody = document.getElementById('stats-top-devices-body');
    
    if (!devices || devices.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #666;">NO DATA AVAILABLE</td></tr>';
        return;
    }
    
    tbody.innerHTML = devices.map(device => `
        <tr>
            <td style="color: var(--accent-cyan); font-weight: 700;">#${device.rank}</td>
            <td style="color: var(--accent-cyan); font-weight: 700;">${device.mac}</td>
            <td>${device.name}</td>
            <td style="color: var(--accent-green); font-weight: 700;">${device.count}</td>
        </tr>
    `).join('');
}

function updateHourlyChart(data) {
    const canvas = document.getElementById('stats-hourly-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, width, height);
    
    if (!data.counts || data.counts.length === 0) {
        ctx.fillStyle = '#666';
        ctx.font = '14px Consolas';
        ctx.textAlign = 'center';
        ctx.fillText('NO DATA AVAILABLE', width / 2, height / 2);
        return;
    }
    
    // Find max value for scaling
    const maxCount = Math.max(...data.counts, 1);
    
    // Draw bars
    const barWidth = width / 24;
    const maxBarHeight = height - 60;
    
    data.counts.forEach((count, i) => {
        const barHeight = (count / maxCount) * maxBarHeight;
        const x = i * barWidth;
        const y = height - barHeight - 30;
        
        // Bar
        ctx.fillStyle = '#6b9bd1';
        ctx.fillRect(x + 2, y, barWidth - 4, barHeight);
        
        // Hour label
        ctx.fillStyle = '#666';
        ctx.font = '10px Consolas';
        ctx.textAlign = 'center';
        ctx.fillText(i + ':00', x + barWidth / 2, height - 10);
        
        // Value label (if > 0)
        if (count > 0) {
            ctx.fillStyle = '#e0e0e0';
            ctx.font = '10px Consolas';
            ctx.fillText(count, x + barWidth / 2, y - 5);
        }
    });
    
    // Peak hour marker
    if (data.peak_hour !== undefined) {
        const peakX = data.peak_hour * barWidth + barWidth / 2;
        ctx.strokeStyle = '#5fbf8a';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(peakX, 10);
        ctx.lineTo(peakX, height - 40);
        ctx.stroke();
        
        ctx.fillStyle = '#5fbf8a';
        ctx.font = '12px Consolas';
        ctx.textAlign = 'center';
        ctx.fillText('PEAK', peakX, 25);
    }
}
