/* HomeNet — Vanilla JS (no framework, Raspberry Pi 3 safe) */
(function() {
  'use strict';

  /* ─── Section Router ─── */
  const sections = document.querySelectorAll('.section');
  const navItems = document.querySelectorAll('.nav-item');
  const currentSectionEl = document.getElementById('currentSection');

  function activateSection(id) {
    sections.forEach(s => s.classList.toggle('active', s.id === id));
    navItems.forEach(n => {
      const active = n.dataset.section === id;
      n.classList.toggle('active', active);
      if (active && currentSectionEl) {
        currentSectionEl.textContent = n.querySelector('span:last-child').textContent;
      }
    });
    // push hash without scroll
    history.replaceState(null, '', '#' + id);
    closeSidebar();
  }

  // Hash routing
  function routeFromHash() {
    const hash = location.hash.replace('#', '') || 'overview';
    const valid = Array.from(sections).some(s => s.id === hash);
    activateSection(valid ? hash : 'overview');
  }
  window.addEventListener('hashchange', routeFromHash);
  routeFromHash();

  // Nav clicks
  document.querySelectorAll('.nav-item, .nav-link').forEach(link => {
    link.addEventListener('click', e => {
      const section = link.dataset.section;
      if (section) { e.preventDefault(); activateSection(section); }
    });
  });

  /* ─── Sidebar Toggle (mobile) ─── */
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('overlay');
  const menuBtn = document.getElementById('menuBtn');
  const sidebarClose = document.getElementById('sidebarClose');

  function openSidebar() {
    sidebar.classList.add('open');
    overlay.classList.add('visible');
    document.body.style.overflow = 'hidden';
  }
  function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.classList.remove('visible');
    document.body.style.overflow = '';
  }

  if (menuBtn) menuBtn.addEventListener('click', openSidebar);
  if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);
  if (overlay) overlay.addEventListener('click', closeSidebar);

  /* ─── Notification Banner ─── */
  function showNotification(msg, type) {
    const bar = document.getElementById('notificationBar');
    const msgEl = document.getElementById('notificationMsg');
    if (!bar || !msgEl) return;
    msgEl.textContent = msg;
    bar.className = 'notification-bar' + (type === 'danger' ? ' danger' : '');
    bar.style.display = 'flex';
    setTimeout(() => { bar.style.display = 'none'; }, 5000);
  }

  /* ─── API Helper ─── */
  async function apiPost(url, onSuccess, onError) {
    try {
      const res = await fetch(url, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      if (res.ok) {
        onSuccess && onSuccess(data);
      } else {
        onError && onError(data.error || 'Error');
      }
    } catch (err) {
      onError && onError(err.message);
    }
  }

  async function apiGet(url, onSuccess, onError) {
    try {
      const res = await fetch(url, { credentials: 'include' });
      const data = await res.json();
      if (res.ok) onSuccess && onSuccess(data);
      else onError && onError(data.error || 'Error');
    } catch (err) {
      onError && onError(err.message);
    }
  }

  /* ─── Scan Hosts ─── */
  window.scanHosts = function() {
    const btn = document.getElementById('scanBtn');
    if (btn) { btn.classList.add('loading'); }
    apiPost(
      '/api/scan_hosts',
      data => {
        showNotification(data.message || 'Scan complete');
        if (btn) btn.classList.remove('loading');
        setTimeout(() => location.reload(), 1500);
      },
      err => {
        showNotification(err, 'danger');
        if (btn) btn.classList.remove('loading');
      }
    );
  };
  const scanBtn = document.getElementById('scanBtn');
  if (scanBtn) scanBtn.addEventListener('click', window.scanHosts);

  /* ─── Setup ─── */
  window.runSetup = function() {
    const setupBtn = document.getElementById('setupBtn');
    if (setupBtn) setupBtn.classList.add('loading');
    const dnsStatus = document.getElementById('dnsStatus');
    const fwStatus = document.getElementById('firewallSetupStatus');
    if (dnsStatus) dnsStatus.textContent = 'Running…';
    if (fwStatus) fwStatus.textContent = 'Running…';

    apiPost(
      '/api/setup',
      data => {
        if (dnsStatus) dnsStatus.textContent = 'DNS: ' + data.dns;
        if (fwStatus) fwStatus.textContent = 'Firewall: ' + data.firewall;
        showNotification(data.message);
        if (setupBtn) setupBtn.classList.remove('loading');
      },
      err => {
        if (dnsStatus) dnsStatus.textContent = 'Error: ' + err;
        showNotification(err, 'danger');
        if (setupBtn) setupBtn.classList.remove('loading');
      }
    );
  };
  const setupBtn = document.getElementById('setupBtn');
  if (setupBtn) setupBtn.addEventListener('click', window.runSetup);

  /* ─── Speed Test ─── */
  window.runSpeedTest = function() {
    const speedStatus = document.getElementById('speedStatus');
    const dl = document.getElementById('dl');
    const ul = document.getElementById('ul');
    const pingEl = document.getElementById('ping');
    const btn = document.getElementById('speedTestBtn');
    const fullBtn = document.getElementById('fullSpeedBtn');

    if (speedStatus) speedStatus.textContent = '…';
    if (dl) dl.textContent = '…';
    if (ul) ul.textContent = '…';
    if (pingEl) pingEl.textContent = '…';
    if (btn) btn.textContent = 'Testing…';
    if (fullBtn) { fullBtn.disabled = true; fullBtn.textContent = 'Testing…'; }

    apiGet(
      '/api/speedtest',
      data => {
        const online = data.status === 'online';
        if (speedStatus) speedStatus.textContent = online ? '●' : '✕';
        if (speedStatus) speedStatus.style.color = online ? 'var(--success)' : 'var(--danger)';
        if (data.speed) {
          if (dl) dl.textContent = data.speed.Download || '—';
          if (ul) ul.textContent = data.speed.Upload || '—';
          if (pingEl) pingEl.textContent = data.speed.Ping || '—';
        }
        if (btn) btn.textContent = data.status === 'online' ? 'Online ●' : 'Offline ✕';
        if (fullBtn) { fullBtn.disabled = false; fullBtn.textContent = 'Test Speed'; }
      },
      err => {
        if (speedStatus) speedStatus.textContent = '✕';
        if (btn) btn.textContent = 'Error';
        if (fullBtn) { fullBtn.disabled = false; fullBtn.textContent = 'Test Speed'; }
        showNotification(err, 'danger');
      }
    );
  };

  const speedTestBtn = document.getElementById('speedTestBtn');
  if (speedTestBtn) speedTestBtn.addEventListener('click', window.runSpeedTest);

  /* ─── Table Filter ─── */
  window.filterTable = function(tableId, query) {
    const table = document.getElementById(tableId);
    if (!table) return;
    const q = query.toLowerCase();
    table.querySelectorAll('tbody tr').forEach(row => {
      row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
  };

  /* ─── Auto-refresh overview stats every 30s ─── */
  if (window.location.hash === '#overview' || !window.location.hash) {
    setInterval(() => {
      apiGet('/api/hosts', data => {
        // Silently update host count stat
        const statValues = document.querySelectorAll('.stat-value');
        if (statValues[0]) statValues[0].textContent = data.length;
      });
    }, 30000);
  }

})();
