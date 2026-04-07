#!/bin/bash
# Start the Screen Extender system
# Run this on the Linux host

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NOVNC_DIR="$HOME/noVNC"

MAC_IP="192.168.50.22"
MAC_VNC_PORT=5900

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Screen Extender - Starting${NC}"

# Step 1: Set up virtual display (if not already)
if ! xrandr | grep -q "DP-0 connected"; then
    echo "Setting up virtual display on DP-0..."
    nvidia-settings --assign CurrentMetaMode="HDMI-0: 1920x1080 +0+0, DP-0: 1440x900 +1920+0" 2>/dev/null || true
fi

# Step 2: Start x0vncserver for the extended screen area
echo -e "${GREEN}Starting VNC server (extended screen)...${NC}"
pkill -f x0vncserver 2>/dev/null || true
sleep 1
x0vncserver FrameRate=30 CompareFB=1 SecurityTypes=none \
    AcceptPointerEvents=True AlwaysShared=on MaxProcessorUsage=70 \
    -geometry 1440x900+1920+0 &
sleep 1

# Step 3: Start noVNC proxy for extended screen (port 6080)
echo -e "${GREEN}Starting noVNC proxy (extended screen on :6080)...${NC}"
pkill -f "novnc_proxy.*6080" 2>/dev/null || true
$NOVNC_DIR/utils/novnc_proxy --vnc localhost:5900 --listen 6080 \
    --cert "$PROJECT_DIR/certs/cert.pem" --key "$PROJECT_DIR/certs/key.pem" &
sleep 1

# Step 4: Start noVNC proxy for Mac remote desktop (port 6081 with TLS)
echo -e "${GREEN}Starting noVNC proxy (Mac remote desktop on :6081)...${NC}"
pkill -f "novnc_proxy.*6081" 2>/dev/null || true
$NOVNC_DIR/utils/novnc_proxy \
    --vnc $MAC_IP:$MAC_VNC_PORT \
    --listen 6081 \
    --cert "$PROJECT_DIR/certs/cert.pem" \
    --key "$PROJECT_DIR/certs/key.pem" &
sleep 1

# Step 5: Serve the web app on port 8080
echo -e "${GREEN}Starting web app on :8080...${NC}"
pkill -f "python.*8080" 2>/dev/null || true

# Serve webapp with noVNC core files accessible
cd "$NOVNC_DIR"
ln -sf "$PROJECT_DIR/webapp/index.html" "$NOVNC_DIR/index.html" 2>/dev/null || true
ln -sf "$PROJECT_DIR/webapp/app.js" "$NOVNC_DIR/app.js" 2>/dev/null || true
ln -sf "$PROJECT_DIR/webapp/style.css" "$NOVNC_DIR/style.css" 2>/dev/null || true

python -c "
import http.server, ssl, os
os.chdir('$NOVNC_DIR')
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain('$PROJECT_DIR/certs/cert.pem', '$PROJECT_DIR/certs/key.pem')
srv = http.server.HTTPServer(('0.0.0.0', 8080), http.server.SimpleHTTPRequestHandler)
srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
srv.serve_forever()
" &
cd "$PROJECT_DIR"

# Step 6: Start the control WebSocket server + control panel
echo -e "${GREEN}Starting control server (:8082 WS, :8083 HTTP)...${NC}"
pkill -f "control.py" 2>/dev/null || true
pip install websockets -q 2>/dev/null || true
python "$PROJECT_DIR/webapp/control.py" &
sleep 1


ssh marcusbader@192.168.50.22 "/Applications/Brave\ Browser\ Beta.app/Contents/MacOS/Brave\ Browser\ Beta --sync https://192.168.50.181:8080 &"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Screen Extender is running!${NC}"
echo ""
echo "  Mac display:    https://192.168.50.181:8080/"
echo "  Linux control:  http://localhost:8083/control.html"
echo ""
echo "  To stop: ./stop.sh"
echo -e "${BLUE}========================================${NC}"

wait
