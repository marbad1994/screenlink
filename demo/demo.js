// State
const state = {
    mac: 'disconnected',  // 'disconnected', 'extended', 'remote'
    win: 'disconnected',
    running: false,
};

// Start the service — animate connection
function startService() {
    if (state.running) return;
    state.running = true;

    // Update widget status
    document.getElementById('widget-status').textContent = 'Online';
    document.getElementById('widget-status').className = 'widget-status online';
    document.getElementById('host-dot').className = 'widget-status-dot online';
    document.getElementById('tray-dot').style.background = '#4CAF50';

    // Animate terminal typing
    const termBody = document.querySelector('.terminal-body');
    termBody.innerHTML = '<div class="terminal-line"><span class="prompt">marcus@desktop:~$</span> screenlink start</div>';

    setTimeout(() => {
        termBody.innerHTML += '<div class="terminal-line dim">Starting ScreenLink...</div>';
    }, 400);

    setTimeout(() => {
        termBody.innerHTML += '<div class="terminal-line dim green">Connected: MacBook Air (192.168.50.22)</div>';
        state.mac = 'extended';
        updateScreens();
        // Show connection line
        document.getElementById('line-right').setAttribute('stroke', 'rgba(76,175,80,0.4)');
    }, 1200);

    setTimeout(() => {
        termBody.innerHTML += '<div class="terminal-line dim green">Connected: Windows Laptop (192.168.50.45)</div>';
        state.win = 'extended';
        updateScreens();
        document.getElementById('line-left').setAttribute('stroke', 'rgba(76,175,80,0.4)');
    }, 2000);

    setTimeout(() => {
        termBody.innerHTML += '<div class="terminal-line"><span class="prompt">marcus@desktop:~$</span> <span class="cursor">_</span></div>';
    }, 2500);

    // Update hint
    document.querySelector('.hint').textContent = 'Click "Remote" to switch a client to remote desktop mode';
}

function stopService() {
    state.running = false;
    state.mac = 'disconnected';
    state.win = 'disconnected';

    document.getElementById('widget-status').textContent = 'Offline';
    document.getElementById('widget-status').className = 'widget-status offline';
    document.getElementById('host-dot').className = 'widget-status-dot offline';
    document.getElementById('tray-dot').style.background = '#f44336';

    document.getElementById('line-left').setAttribute('stroke', 'rgba(76,175,80,0)');
    document.getElementById('line-right').setAttribute('stroke', 'rgba(76,175,80,0)');

    const termBody = document.querySelector('.terminal-body');
    termBody.innerHTML = '<div class="terminal-line"><span class="prompt">marcus@desktop:~$</span> screenlink stop</div>';
    termBody.innerHTML += '<div class="terminal-line dim">Stopped.</div>';
    termBody.innerHTML += '<div class="terminal-line"><span class="prompt">marcus@desktop:~$</span> <span class="cursor">_</span></div>';

    updateScreens();
    document.querySelector('.hint').textContent = 'Click the ScreenLink icon in the taskbar, then press \u25B6 to connect';
}

function restartService() {
    stopService();
    setTimeout(startService, 800);
}

function toggleMode(client) {
    if (!state.running) return;
    if (state[client] === 'disconnected') return;

    if (state[client] === 'extended') {
        state[client] = 'remote';
    } else {
        state[client] = 'extended';
    }
    updateScreens();
}

function updateScreens() {
    updateClient('mac', 'right-screen', 'mac-mode-label', 'mac-btn-text', 'mac-toggle');
    updateClient('win', 'left-screen', 'win-mode-label', 'win-btn-text', 'win-toggle');
}

function updateClient(client, screenId, labelId, btnId, toggleId) {
    const screen = document.getElementById(screenId);
    const label = document.getElementById(labelId);
    const btn = document.getElementById(btnId);
    const toggle = document.getElementById(toggleId);

    // Clear overlays
    screen.querySelectorAll('.extended-overlay, .remote-overlay-indicator').forEach(el => el.remove());

    if (state[client] === 'disconnected') {
        label.textContent = 'Disconnected';
        label.className = 'widget-item-name disconnected-label';
        btn.textContent = '—';
        toggle.className = 'widget-mode-btn disabled';
        return;
    }

    label.className = 'widget-item-name';
    toggle.className = 'widget-mode-btn';

    if (state[client] === 'extended') {
        label.textContent = 'Extended Screen';
        btn.textContent = 'Remote';

        const overlay = document.createElement('div');
        overlay.className = 'extended-overlay';
        overlay.innerHTML = `
            <div class="extended-content">
                <div class="extended-badge">EXTENDED</div>
                ${client === 'mac' ? `
                    <div class="extended-window" style="top:22px;left:12px;width:130px;height:75px;">
                        <div class="ext-win-titlebar">
                            <div class="ext-win-dot" style="background:#e74c3c"></div>
                            <div class="ext-win-dot" style="background:#f39c12"></div>
                            <div class="ext-win-dot" style="background:#2ecc71"></div>
                        </div>
                        <div class="ext-win-body">
                            $ npm run dev<br>
                            Server running on :3000<br>
                            Watching for changes...
                        </div>
                    </div>
                    <div class="extended-window" style="top:40px;left:100px;width:120px;height:70px;">
                        <div class="ext-win-titlebar">
                            <div class="ext-win-dot" style="background:#e74c3c"></div>
                            <div class="ext-win-dot" style="background:#f39c12"></div>
                            <div class="ext-win-dot" style="background:#2ecc71"></div>
                        </div>
                        <div class="ext-win-body" style="background:#1a1a2e;color:#7c4dff;">
                            function App() {<br>
                            &nbsp;&nbsp;return (<br>
                            &nbsp;&nbsp;&nbsp;&nbsp;&lt;div&gt;...<br>
                        </div>
                    </div>
                ` : `
                    <div class="extended-window" style="top:20px;left:15px;width:140px;height:80px;">
                        <div class="ext-win-titlebar">
                            <div class="ext-win-dot" style="background:#e74c3c"></div>
                            <div class="ext-win-dot" style="background:#f39c12"></div>
                            <div class="ext-win-dot" style="background:#2ecc71"></div>
                        </div>
                        <div class="ext-win-body" style="background:#111827;">
                            <div style="color:#4CAF50;font-size:6px;">Dashboard</div>
                            <div style="display:flex;gap:3px;margin-top:3px;">
                                <div style="width:20px;height:15px;background:rgba(76,175,80,0.2);border-radius:2px;"></div>
                                <div style="width:20px;height:15px;background:rgba(33,150,243,0.2);border-radius:2px;"></div>
                                <div style="width:20px;height:15px;background:rgba(124,77,255,0.2);border-radius:2px;"></div>
                            </div>
                        </div>
                    </div>
                `}
            </div>
        `;
        screen.appendChild(overlay);
    } else {
        label.textContent = 'Remote Desktop';
        btn.textContent = 'Extend';

        const badge = document.createElement('div');
        badge.className = 'remote-overlay-indicator';
        badge.style.cssText = `
            position:absolute;top:${client === 'mac' ? '20' : '6'}px;left:6px;
            font-size:5.5px;color:rgba(33,150,243,0.9);
            background:rgba(33,150,243,0.1);padding:2px 5px;
            border-radius:3px;border:1px solid rgba(33,150,243,0.2);
            z-index:10;
        `;
        badge.textContent = 'REMOTE CONTROL';
        screen.appendChild(badge);
    }
}

// Init — everything starts disconnected
updateScreens();
document.getElementById('widget-status').textContent = 'Offline';
document.getElementById('widget-status').className = 'widget-status offline';
document.getElementById('host-dot').className = 'widget-status-dot offline';
document.getElementById('tray-dot').style.background = '#f44336';

// Widget popup toggle via tray icon
document.getElementById('tray-icon').addEventListener('click', (e) => {
    e.stopPropagation();
    document.getElementById('widget-popup').classList.toggle('visible');
});

document.addEventListener('click', (e) => {
    const popup = document.getElementById('widget-popup');
    if (!popup.contains(e.target) && !document.getElementById('tray-icon').contains(e.target)) {
        popup.classList.remove('visible');
    }
});

document.getElementById('widget-popup').addEventListener('click', (e) => {
    e.stopPropagation();
});
