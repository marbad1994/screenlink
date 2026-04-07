// Extended screen + control channel
const CONFIG = {
    extendedWSUrl: 'wss://192.168.50.181:6080/websockify',
    controlWSUrl: 'wss://192.168.50.181:8082',
};

import RFB from '/core/rfb.js';

let rfb = null;
let controlWs = null;
let active = true;

function connectExtended() {
    if (!active) return;
    const container = document.getElementById('screen');
    container.innerHTML = '';
    try {
        rfb = new RFB(container, CONFIG.extendedWSUrl, {
            scaleViewport: true,
            resizeSession: false,
            showDotCursor: true,
        });
        rfb.viewOnly = true;
        rfb.addEventListener('disconnect', () => {
            rfb = null;
            if (active) setTimeout(connectExtended, 3000);
        });
    } catch (e) {
        if (active) setTimeout(connectExtended, 3000);
    }
}

function disconnectExtended() {
    if (rfb) {
        rfb.disconnect();
        rfb = null;
    }
    const container = document.getElementById('screen');
    container.innerHTML = '';
}

function connectControl() {
    controlWs = new WebSocket(CONFIG.controlWSUrl);
    controlWs.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.mode === 'remote') {
            active = false;
            disconnectExtended();
        }else if (data.mode === 'extended') {
            active = true;
            connectExtended();
        } 
    };
    controlWs.onclose = () => setTimeout(connectControl, 2000);
    controlWs.onerror = () => controlWs.close();
}

connectControl();
connectExtended();
