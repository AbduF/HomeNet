/**
 * HomeNet 2026 - Modern Frontend Module
 * Features: Micro-interactions, AI suggestions, real-time updates, accessibility
 */

class HomeNetApp {
  constructor(config) {
    this.config = config;
    this.lang = document.documentElement.lang || 'en';
    this.isRTL = document.documentElement.dir === 'rtl';
    this.init();
  }

  init() {
    this.setupThemeToggle();
    this.setupMicroInteractions();
    this.initCharts();
    this.setupQuickActions();
    this.loadSmartSuggestions();
    this.setupRealTimeUpdates();
    this.bindAccessibility();
    console.log(`🚀 HomeNet ${this.config.app_version} initialized`);
  }

  // 🌓 Theme Management with Persistence
  setupThemeToggle() {
    const toggle = document.getElementById('themeToggle');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Load saved preference or use system
    const savedTheme = localStorage.getItem('homenet-theme');
    const currentTheme = savedTheme || (prefersDark.matches ? 'dark' : 'light');
    
    this.applyTheme(currentTheme);
    
    if (toggle) {
      toggle.checked = currentTheme === 'dark';
      toggle.addEventListener('change', (e) => {
        const theme = e.target.checked ? 'dark' : 'light';
        this.applyTheme(theme);
        localStorage.setItem('homenet-theme', theme);
        
        // Haptic feedback for touch devices
        if ('vibrate' in navigator) navigator.vibrate(10);
      });
    }
    
    // Listen for system theme changes
    prefersDark.addEventListener('change', (e) => {
      if (!localStorage.getItem('homenet-theme')) {
        this.applyTheme(e.matches ? 'dark' : 'light');
      }
    });
  }

  applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', 
      theme === 'dark' ? '#0f172a' : '#6366f1');
  }

  // 🎭 Micro-Interactions System
  setupMicroInteractions() {
    // Elastic hover for buttons
    document.querySelectorAll('.btn').forEach(btn => {
      btn.addEventListener('mouseenter', (e) => {
        e.currentTarget.style.transform = 'translateY(-1px)';
      });
      btn.addEventListener('mouseleave', (e) => {
        e.currentTarget.style.transform = '';
      });
      btn.addEventListener('touchstart', (e) => {
        if ('vibrate' in navigator) navigator.vibrate(5);
      }, { passive: true });
    });

    // Card hover lift
    document.querySelectorAll('.card-glass').forEach(card => {
      card.addEventListener('mouseenter', (e) => {
        e.currentTarget.style.zIndex = '1';
      });
      card.addEventListener('mouseleave', (e) => {
        e.currentTarget.style.zIndex = '';
      });
    });

    // Skeleton loading for dynamic content
    this.showSkeleton = (container, rows = 3) => {
      container.innerHTML = Array(rows).fill(`
        <div class="flex items-center gap-3 p-3">
          <div class="skeleton rounded-full" style="width:2rem;height:2rem"></div>
          <div class="flex-1">
            <div class="skeleton skeleton-text w-60"></div>
            <div class="skeleton skeleton-text w-40 mt-2"></div>
          </div>
        </div>
      `).join('');
    };
  }

  // 📊 Chart.js Initialization
  initCharts() {
    const ctx = document.getElementById('trafficChart');
    if (!ctx) return;

    const chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [], // Will be populated dynamically
        datasets: [{
          label: 'Download (MB)',
          data: [],
          borderColor: 'oklch(0.65 0.22 265)',
          backgroundColor: 'oklch(0.65 0.22 265 / 0.1)',
          tension: 0.4,
          fill: true,
          pointRadius: 0,
          pointHoverRadius: 4
        }, {
          label: 'Upload (MB)',
          data: [],
          borderColor: 'oklch(0.72 0.15 150)',
          backgroundColor: 'oklch(0.72 0.15 150 / 0.1)',
          tension: 0.4,
          fill: true,
          pointRadius: 0,
          pointHoverRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 750, easing: 'easeOutQuart' },
        plugins: {
          legend: { 
            position: 'top', 
            labels: { 
              usePointStyle: true,
              padding: 20,
              font: { size: 12 }
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: 'oklch(0.2 0.02 260 / 0.9)',
            titleColor: 'white',
            bodyColor: 'oklch(0.95 0.01 260)',
            padding: 12,
            cornerRadius: 8
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: 'oklch(0.45 0.02 260)', font: { size: 11 } }
          },
          y: {
            beginAtZero: true,
            grid: { color: 'oklch(0.9 0.01 260 / 0.3)' },
            ticks: { color: 'oklch(0.45 0.02 260)', font: { size: 11 } }
          }
        },
        interaction: { mode: 'nearest', axis: 'x', intersect: false }
      }
    });

    // Populate with sample data (replace with real API fetch)
    this.populateTrafficChart(chart);
    
    // Store for real-time updates
    window.trafficChart = chart;
  }

  populateTrafficChart(chart) {
    // Generate realistic sample data
    const now = new Date();
    const labels = Array.from({length: 24}, (_, i) => {
      const d = new Date(now - (23 - i) * 60 * 60 * 1000);
      return d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    });
    
    const download = Array.from({length: 24}, () => Math.random() * 50 + 10);
    const upload = Array.from({length: 24}, () => Math.random() * 20 + 5);
    
    chart.data.labels = labels;
    chart.data.datasets[0].data = download;
    chart.data.datasets[1].data = upload;
    chart.update('none'); // 'none' for instant update without animation
  }

  // ⚡ Quick Actions Handler
  setupQuickActions() {
    document.querySelectorAll('[data-action]').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const action = e.currentTarget.dataset.action;
        const originalText = e.currentTarget.innerHTML;
        
        // Loading state
        e.currentTarget.disabled = true;
        e.currentTarget.innerHTML = `<span class="loading-spinner"></span> Processing...`;
        
        try {
          switch(action) {
            case 'scan':
              await this.scanNetwork();
              break;
            case 'peak-hours':
              await this.togglePeakHours();
              break;
            case 'export':
              this.exportLogs();
              break;
          }
          
          // Success feedback
          if ('vibrate' in navigator) navigator.vibrate([10, 5, 10]);
          this.showToast('Action completed!', 'success');
          
        } catch (error) {
          console.error(`Action ${action} failed:`, error);
          this.showToast('Action failed. Check logs.', 'error');
        } finally {
          // Restore button
          e.currentTarget.disabled = false;
          e.currentTarget.innerHTML = originalText;
        }
      });
    });
  }

  async scanNetwork() {
    const response = await fetch('/api/scan_hosts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error('Scan failed');
    const data = await response.json();
    
    // Update UI
    document.getElementById('active-hosts').textContent = 
      parseInt(document.getElementById('active-hosts').textContent) + data.found || 0;
    
    // Refresh hosts table
    await this.refreshHostsTable();
  }

  async togglePeakHours() {
    // Implementation for time-based blocking toggle
    const response = await fetch('/api/setup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enable_peak_hours: true })
    });
    if (!response.ok) throw new Error('Failed to update settings');
  }

  exportLogs() {
    // Create downloadable CSV
    const csv = this.generateCSV(window.HomeNetData.hosts);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `homenet-logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  generateCSV(data) {
    if (!data.length) return '';
    const headers = Object.keys(data[0]).join(',');
    const rows = data.map(row => 
      Object.values(row).map(v => `"${String(v).replace(/"/g, '""')}"`).join(',')
    ).join('\n');
    return `${headers}\n${rows}`;
  }

  // 🤖 AI Smart Suggestions (Client-side Pattern Matching)
  async loadSmartSuggestions() {
    const container = document.getElementById('suggestions-list');
    if (!container) return;

    try {
      // Simulate AI analysis (replace with real endpoint)
      const suggestions = await this.analyzeUserPatterns();
      
      if (suggestions.length === 0) {
        container.innerHTML = `<p class="text-sm text-secondary">No suggestions at this time.</p>`;
        return;
      }

      container.innerHTML = suggestions.map(s => `
        <div class="suggestion-item p-4 rounded-lg border border-border-subtle hover:border-primary transition-colors cursor-pointer"
             data-action="${s.action}" role="button" tabindex="0">
          <div class="flex items-start gap-3">
            <span class="text-xl mt-0.5" aria-hidden="true">${s.icon}</span>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-sm">${s.title}</p>
              <p class="text-xs text-secondary mt-1">${s.description}</p>
            </div>
            <span class="text-primary text-sm font-medium">Apply →</span>
          </div>
        </div>
      `).join('');

      // Bind click handlers
      container.querySelectorAll('[data-action]').forEach(item => {
        item.addEventListener('click', (e) => {
          const action = e.currentTarget.dataset.action;
          this.applySuggestion(action);
        });
        // Keyboard accessibility
        item.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            item.click();
          }
        });
      });

    } catch (error) {
      console.warn('Failed to load suggestions:', error);
      container.innerHTML = `<p class="text-sm text-error">Unable to load suggestions</p>`;
    }
  }

  async analyzeUserPatterns() {
    // Client-side pattern analysis (privacy-preserving)
    const patterns = JSON.parse(localStorage.getItem('homenet_patterns') || '{}');
    const hour = new Date().getHours();
    const suggestions = [];

    // Time-based suggestions
    if (hour >= 20 && hour < 22 && !patterns.peakHoursEnabled) {
      suggestions.push({
        icon: '🌙',
        title: 'Enable Evening Focus Mode',
        description: 'Auto-block social media 10 PM - 6 AM for better sleep',
        action: 'enable-peak-hours',
        priority: 'high'
      });
    }

    // New device detection pattern
    const recentHosts = window.HomeNetData.hosts?.filter(h => {
      const seen = new Date(h.last_seen);
      return (Date.now() - seen) < 24 * 60 * 60 * 1000; // Last 24h
    }) || [];
    
    if (recentHosts.length > 3 && !patterns.newDeviceReviewed) {
      suggestions.push({
        icon: '🔍',
        title: 'Review New Devices',
        description: `${recentHosts.length} new devices detected today`,
        action: 'review-devices',
        priority: 'medium'
      });
    }

    // Sort by priority
    return suggestions.sort((a, b) => 
      ({high:3, medium:2, low:1}[b.priority] - {high:3, medium:2, low:1}[a.priority])
    );
  }

  applySuggestion(action) {
    // Handle suggestion actions
    switch(action) {
      case 'enable-peak-hours':
        this.togglePeakHours();
        break;
      case 'review-devices':
        document.getElementById('hosts-section')?.scrollIntoView({ behavior: 'smooth' });
        break;
    }
    
    // Track interaction (anonymized)
    const patterns = JSON.parse(localStorage.getItem('homenet_patterns') || '{}');
    patterns[`${action}Clicked`] = true;
    localStorage.setItem('homenet_patterns', JSON.stringify(patterns));
  }

  // 📡 Real-time Updates (WebSocket fallback to polling)
  setupRealTimeUpdates() {
    if (this.config.ws_enabled && 'WebSocket' in window) {
      this.setupWebSocket();
    } else {
      // Fallback to polling
      setInterval(() => this.pollForUpdates(), 30000); // 30s
    }
  }

  setupWebSocket() {
    const ws = new WebSocket(`ws://${window.location.host}/ws/updates`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleRealtimeUpdate(data);
    };
    
    ws.onclose = () => {
      console.warn('WebSocket closed, falling back to polling');
      setInterval(() => this.pollForUpdates(), 30000);
    };
  }

  async pollForUpdates() {
    try {
      const response = await fetch('/api/updates?since=' + Date.now());
      if (response.ok) {
        const data = await response.json();
        this.handleRealtimeUpdate(data);
      }
    } catch (error) {
      console.debug('Polling update failed (expected on first load):', error);
    }
  }

  handleRealtimeUpdate(data) {
    // Update traffic chart if new data
    if (data.traffic?.length) {
      this.updateTrafficChart(data.traffic);
    }
    
    // Update alerts preview
    if (data.new_alerts?.length) {
      this.prependAlerts(data.new_alerts);
      this.showToast(`${data.new_alerts.length} new alert${data.new_alerts.length>1?'s':''}`, 'info');
    }
    
    // Update host count
    if (data.host_count !== undefined) {
      document.getElementById('active-hosts').textContent = data.host_count;
    }
  }

  updateTrafficChart(newPoints) {
    const chart = window.trafficChart;
    if (!chart) return;
    
    // Add new data points, remove old ones to maintain 24h window
    chart.data.labels.push(new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}));
    chart.data.datasets[0].data.push(newPoints.download || 0);
    chart.data.datasets[1].data.push(newPoints.upload || 0);
    
    // Keep only last 24 points
    if (chart.data.labels.length > 24) {
      chart.data.labels.shift();
      chart.data.datasets.forEach(ds => ds.data.shift());
    }
    
    chart.update('none');
  }

  prependAlerts(alerts) {
    const container = document.getElementById('alerts-preview');
    if (!container) return;
    
    alerts.forEach(alert => {
      const el = document.createElement('div');
      el.className = 'alert-item flex items-start gap-3 p-3 rounded-lg bg-surface-alt animate-fade-in';
      el.innerHTML = `
        <span class="text-lg" aria-hidden="true">
          ${alert.type === 'new_host' ? '🆕' : alert.type === 'blocked' ? '🚫' : '⚠️'}
        </span>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium truncate">${alert.message}</p>
          <p class="text-xs text-secondary">${new Date(alert.timestamp).toLocaleTimeString()}</p>
        </div>
      `;
      container.insertBefore(el, container.firstChild);
      
      // Limit to 5 visible
      if (container.children.length > 5) {
        container.removeChild(container.lastChild);
      }
    });
  }

  // 🔔 Toast Notifications
  showToast(message, type = 'info', duration = 3000) {
    // Remove existing toasts
    document.querySelectorAll('.toast').forEach(t => t.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast fixed bottom-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg 
      ${type === 'success' ? 'bg-success text-white' : 
        type === 'error' ? 'bg-error text-white' : 
        'bg-surface border border-border-subtle'}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'polite');
    toast.innerHTML = `
      <div class="flex items-center gap-3">
        <span aria-hidden="true">
          ${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}
        </span>
        <span class="text-sm font-medium">${message}</span>
        <button class="ml-2 text-lg opacity-70 hover:opacity-100" 
                aria-label="Dismiss notification"
                onclick="this.closest('.toast').remove()">×</button>
      </div>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-dismiss
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.2s ease';
      setTimeout(() => toast.remove(), 200);
    }, duration);
    
    // Haptic feedback
    if ('vibrate' in navigator) {
      navigator.vibrate(type === 'error' ? [20, 10, 20] : 10);
    }
  }

  // ♿ Accessibility Enhancements
  bindAccessibility() {
    // Skip link functionality
    const skipLink = document.querySelector('.skip-link');
    if (skipLink) {
      skipLink.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelector('main')?.focus();
      });
    }
    
    // Keyboard navigation for cards
    document.querySelectorAll('.card-glass[tabindex]').forEach(card => {
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          card.querySelector('button')?.click();
        }
      });
    });
    
    // Announce dynamic updates to screen readers
    this.announce = (message) => {
      const liveRegion = document.getElementById('aria-live-region') || 
        (() => {
          const el = document.createElement('div');
          el.id = 'aria-live-region';
          el.setAttribute('aria-live', 'polite');
          el.setAttribute('aria-atomic', 'true');
          el.className = 'sr-only';
          document.body.appendChild(el);
          return el;
        })();
      liveRegion.textContent = message;
    };
  }

  // Utility: Refresh hosts table
  async refreshHostsTable() {
    const container = document.querySelector('#hosts-section table tbody');
    if (!container) return;
    
    this.showSkeleton(container, 5);
    
    try {
      const response = await fetch('/api/hosts?page=1&per_page=10');
      const hosts = await response.json();
      
      container.innerHTML = hosts.map(host => `
        <tr>
          <td><code class="text-sm">${host.ip}</code></td>
          <td><code class="text-sm">${host.mac}</code></td>
          <td>${host.hostname || '-'}</td>
          <td>${host.os || '-'}</td>
          <td><time datetime="${host.last_seen}">${new Date(host.last_seen).toLocaleString()}</time></td>
          <td>
            <button class="btn-icon btn-sm" aria-label="View details">⋮</button>
          </td>
        </tr>
      `).join('') || `<tr><td colspan="6" class="text-center py-8 text-secondary">No hosts found</td></tr>`;
      
      this.announce('Hosts list refreshed');
    } catch (error) {
      console.error('Failed to refresh hosts:', error);
      this.showToast('Failed to refresh hosts', 'error');
    }
  }
}

// ✅ Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  if (window.HomeNetConfig) {
    window.homenet = new HomeNetApp(window.HomeNetConfig);
  }
});

// ✅ Global functions for inline handlers (legacy support)
window.refreshHosts = () => window.homenet?.refreshHostsTable();
window.scanHosts = () => document.querySelector('[data-action="scan"]')?.click();