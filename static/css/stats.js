/**
 * NoctisCore - STATS Module
 * ==========================
 * Charts, Analytics, Time Filters
 */

// ========================= STATE =========================

const state = {
    timeFilter: 'all',
    charts: {},
    data: null
};

// ========================= INITIALIZATION =========================

document.addEventListener('DOMContentLoaded', () => {
    console.log('STATS Module initialized');
    
    // Initialize
    initFilters();
    initButtons();
    loadStats();
    
    // Auto-refresh every 30 seconds
    setInterval(loadStats, 30000);
});

// ========================= FILTERS =========================

function initFilters() {
    const filterItems = document.querySelectorAll('[data-filter="time"]');
    
    filterItems.forEach(item => {
        item.addEventListener('click', () => {
            const value = item.dataset.value;
            
            // Update UI
            filterItems.forEach(f => {
                const checkbox = f.querySelector('.filter-checkbox');
                checkbox.classList.remove('checked');
                checkbox.textContent = '';
                f.classList.remove('active');
            });
            
            const checkbox = item.querySelector('.filter-checkbox');
            checkbox.classList.add('checked');
            checkbox.textContent = '✓';
            item.classList.add('active');
            
            // Update state
            state.timeFilter = value;
            
            // Reload data
            loadStats();
        });
    });
}

// ========================= BUTTONS =========================

function initButtons() {
    const refreshBtn = document.getElementById('refresh-btn');
    const exportCsvBtn = document.getElementById('export-csv-btn');
    const exportJsonBtn = document.getElementById('export-json-btn');
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            loadStats();
        });
    }
    
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', () => {
            exportData('csv');
        });
    }
    
    if (exportJsonBtn) {
        exportJsonBtn.addEventListener('click', () => {
            exportData('json');
        });
    }
}

// ========================= LOAD STATS =========================

async function loadStats() {
    console.log('Loading stats with filter:', state.timeFilter);
    
    try {
        const timeParam = state.timeFilter === 'all' ? '' : `?time_filter=${state.timeFilter}`;
        
        // Load all stats
        const [overview, topDevices, hourly, daily, weekday, heatmap, extended] = await Promise.all([
            fetch(`/api/stats/overview${timeParam}`).then(r => r.json()),
            fetch(`/api/stats/top-devices${timeParam}`).then(r => r.json()),
            fetch(`/api/stats/hourly${timeParam}`).then(r => r.json()),
            fetch(`/api/stats/daily${timeParam}`).then(r => r.json()),
            fetch(`/api/stats/weekday${timeParam}`).then(r => r.json()),
            fetch(`/api/stats/heatmap${timeParam}`).then(r => r.json()),
            fetch(`/api/stats/extended${timeParam}`).then(r => r.json())
        ]);
        
        state.data = {
            overview,
            topDevices,
            hourly,
            daily,
            weekday,
            heatmap,
            extended
        };
        
        // Update UI
        updateOverviewCards(overview);
        updateSidebar(overview);
        updateTopDevicesTable(topDevices);
        updateLifetimeStats(extended.lifetime);
        
        // Update Charts
        updateHourlyChart(hourly);
        updateDailyChart(daily);
        updateWeekdayChart(weekday);
        updateHeatmapChart(heatmap);
        updateRssiChart(extended.rssi);
        updateOuiChart(extended.oui);
        updateProtocolChart(extended.protocol);
        
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// ========================= UPDATE UI =========================

function updateOverviewCards(data) {
    document.getElementById('stat-total').textContent = data.total_scans || 0;
    document.getElementById('stat-unique').textContent = data.unique_devices || 0;
    document.getElementById('stat-24h').textContent = data.last_24h || 0;
    document.getElementById('stat-1h').textContent = data.last_hour || 0;
}

function updateSidebar(data) {
    document.getElementById('sidebar-total').textContent = data.total_scans || 0;
    document.getElementById('sidebar-unique').textContent = data.unique_devices || 0;
    document.getElementById('sidebar-24h').textContent = data.last_24h || 0;
    document.getElementById('sidebar-1h').textContent = data.last_hour || 0;
}

function updateTopDevicesTable(data) {
    const tbody = document.getElementById('top-devices-table');
    
    if (!data.devices || data.devices.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No devices found</td></tr>';
        return;
    }
    
    tbody.innerHTML = data.devices.map(device => {
        const share = ((device.count / data.total) * 100).toFixed(1);
        const vendor = lookupOui(device.mac);
        
        return `
            <tr>
                <td style="color: var(--accent-cyan); font-weight: 700;">#${device.rank}</td>
                <td style="color: var(--accent-cyan); font-family: 'Consolas', monospace;">${device.mac}</td>
                <td>${device.name}</td>
                <td>${vendor}</td>
                <td style="font-family: 'Consolas', monospace;">${device.count}</td>
                <td style="color: var(--accent-green);">${share}%</td>
            </tr>
        `;
    }).join('');
}

function updateLifetimeStats(data) {
    document.getElementById('lifetime-avg').textContent = `${data.avg_lifetime_minutes} min`;
    document.getElementById('lifetime-median').textContent = `${data.median_lifetime_minutes} min`;
    document.getElementById('lifetime-max').textContent = `${data.max_lifetime_minutes} min`;
    document.getElementById('lifetime-multi').textContent = data.devices_with_multiple_sightings;
}

// ========================= CHARTS =========================

// Chart.js Global Config
Chart.defaults.color = '#a0a0a0';
Chart.defaults.borderColor = '#333333';
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, Inter, Segoe UI';
Chart.defaults.font.size = 11;

function updateHourlyChart(data) {
    const ctx = document.getElementById('hourly-chart');
    
    if (state.charts.hourly) {
        state.charts.hourly.destroy();
    }
    
    // Update peak hour
    document.getElementById('peak-hour').textContent = `${data.peak_hour}:00`;
    
    state.charts.hourly = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.hours.map(h => `${h}:00`),
            datasets: [{
                label: 'Devices',
                data: data.counts,
                borderColor: '#6b9bd1',
                backgroundColor: 'rgba(107, 155, 209, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#1a1a1a'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function updateDailyChart(data) {
    const ctx = document.getElementById('daily-chart');
    
    if (state.charts.daily) {
        state.charts.daily.destroy();
    }
    
    // Update max day
    document.getElementById('max-day').textContent = data.max_day || '--';
    
    state.charts.daily = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.dates,
            datasets: [{
                label: 'Scans',
                data: data.counts,
                backgroundColor: '#5fbf8a',
                borderColor: '#5fbf8a',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#1a1a1a'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function updateWeekdayChart(data) {
    const ctx = document.getElementById('weekday-chart');
    
    if (state.charts.weekday) {
        state.charts.weekday.destroy();
    }
    
    // Update most active day
    document.getElementById('most-active-day').textContent = data.most_active || '--';
    
    state.charts.weekday = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.weekdays,
            datasets: [{
                label: 'Scans',
                data: data.counts,
                backgroundColor: '#e5c07b',
                borderColor: '#e5c07b',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#1a1a1a'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function updateRssiChart(data) {
    const ctx = document.getElementById('rssi-chart');
    
    if (state.charts.rssi) {
        state.charts.rssi.destroy();
    }
    
    // Update median
    document.getElementById('rssi-median').textContent = data.median || '--';
    
    state.charts.rssi = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.bins.map(b => `${b} dBm`),
            datasets: [{
                label: 'Count',
                data: data.counts,
                backgroundColor: '#d96c75',
                borderColor: '#d96c75',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#1a1a1a'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function updateOuiChart(data) {
    const ctx = document.getElementById('oui-chart');
    
    if (state.charts.oui) {
        state.charts.oui.destroy();
    }
    
    // Update vendor count
    document.getElementById('vendor-count').textContent = data.total_devices || 0;
    
    const colors = ['#6b9bd1', '#5fbf8a', '#e5c07b', '#d96c75', '#a0a0a0', '#666666'];
    
    state.charts.oui = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.vendors.map(v => v.name),
            datasets: [{
                data: data.vendors.map(v => v.count),
                backgroundColor: colors,
                borderColor: '#000000',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 10
                    }
                }
            }
        }
    });
}

function updateProtocolChart(data) {
    const ctx = document.getElementById('protocol-chart');
    
    if (state.charts.protocol) {
        state.charts.protocol.destroy();
    }
    
    // Update protocol total
    document.getElementById('protocol-total').textContent = data.total || 0;
    
    const colors = ['#6b9bd1', '#5fbf8a', '#e5c07b'];
    
    state.charts.protocol = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.protocols.map(p => p.name),
            datasets: [{
                data: data.protocols.map(p => p.count),
                backgroundColor: colors,
                borderColor: '#000000',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 10
                    }
                }
            }
        }
    });
}

function updateHeatmapChart(data) {
    const ctx = document.getElementById('heatmap-chart');
    
    if (state.charts.heatmap) {
        state.charts.heatmap.destroy();
    }
    
    // Transform matrix to Chart.js format
    const datasets = data.weekdays.map((day, dayIdx) => {
        return {
            label: day,
            data: data.hours.map((hour, hourIdx) => ({
                x: hour,
                y: dayIdx,
                v: data.matrix[hourIdx][dayIdx]
            })),
            backgroundColor: function(context) {
                const value = context.dataset.data[context.dataIndex].v;
                const maxValue = Math.max(...data.matrix.flat());
                const alpha = value / maxValue;
                return `rgba(107, 155, 209, ${alpha})`;
            },
            borderWidth: 1,
            borderColor: '#000000'
        };
    });
    
    state.charts.heatmap = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Hour ${context.parsed.x}:00, ${data.weekdays[context.parsed.y]}: ${context.raw.v} devices`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    min: 0,
                    max: 23,
                    ticks: {
                        stepSize: 1
                    },
                    title: {
                        display: true,
                        text: 'Hour of Day'
                    },
                    grid: {
                        color: '#1a1a1a'
                    }
                },
                y: {
                    type: 'linear',
                    min: 0,
                    max: 6,
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            return data.weekdays[value] || '';
                        }
                    },
                    title: {
                        display: true,
                        text: 'Day of Week'
                    },
                    grid: {
                        color: '#1a1a1a'
                    }
                }
            }
        }
    });
}

// ========================= EXPORT =========================

async function exportData(format) {
    try {
        const timeParam = state.timeFilter === 'all' ? '' : `?time_filter=${state.timeFilter}`;
        const response = await fetch(`/api/export/${format}${timeParam}`);
        const blob = await response.blob();
        
        // Download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `noctis_stats_${Date.now()}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        console.log(`Exported as ${format}`);
    } catch (error) {
        console.error('Export error:', error);
    }
}

// ========================= UTILS =========================

function lookupOui(mac) {
    // Simple OUI lookup (first 8 chars)
    const oui = mac.substring(0, 8).toUpperCase();
    
    const ouiMap = {
        '00:03:93': 'Apple',
        '00:05:02': 'Apple',
        '00:0A:27': 'Apple',
        '00:0A:95': 'Apple',
        '0C:47:C9': 'Samsung',
        '10:08:B1': 'Samsung',
        '00:0C:F1': 'Intel',
        '00:13:E0': 'Intel',
        '00:50:F2': 'Microsoft'
    };
    
    return ouiMap[oui] || 'Unknown';
}
