#!/usr/bin/env python3
"""
Control server: toggles between Extended and Remote Desktop modes.

Extended:  Mac Chrome fullscreen (noVNC showing Linux extended screen)
Remote:    Mac Chrome hidden, TigerVNC viewer opens on Linux showing Mac screen
"""

import asyncio
import json
import ssl
import os
import subprocess
import http.server
import threading
import websockets



CERT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'certs')
CERT = os.path.join(CERT_DIR, 'cert.pem')
KEY = os.path.join(CERT_DIR, 'key.pem')

PORT_WS = 8082
PORT_WS_LOCAL = 8085
PORT_HTTP = 8083

MAC_SSH = "marcusbader@192.168.50.22"
MAC_VNC = "192.168.50.22:5900"
REMOTE_URL = "https://192.168.50.181:8080/remote.html"

clients = set()
current_mode = "extended"
vncviewer_proc = None

def get_brave(brave, url, pre=[], post=[]):
    command = f"{brave} --sync --new-window ";
    return_string = command + url;
    return pre + return_string.split(" ") + post;


def switch_to_extended():
    """Close Linux remote browser, open fresh Chrome on Mac."""
    global vncviewer_proc
    # Kill remote desktop browser on Linux
    if vncviewer_proc:
        vncviewer_proc.terminate()
        vncviewer_proc = None
    # subprocess.run(["killall", "brave"], capture_output=True)

    try:
        subprocess.Popen(
            ["ssh", "-o", "ConnectTimeout=5", MAC_SSH,
                """i=0; while [ $i -le 5 ]; do exd=$(lsof -i udp | grep Brave | awk '{print $2}'); if [ -n "$exd" ]; then kill $(echo "$exd" | head -n 1); i=0; fi; sleep 1; i=$((i + 1)); done"""  ],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
    except Exception as e:
        print(f"SSH error: {e}")
    # Open fresh Chrome on Mac with the extended screen page
    open_windows = subprocess.check_output(["wmctrl", "-l"], text=True)
    if "Screen Extender" not in open_windows:
        try:
            subprocess.Popen(
                get_brave("/Applications/Brave\ Browser\ Beta.app/Contents/MacOS/Brave\ Browser\ Beta", "https://192.168.50.181:8080/  --args --start-fullscreen", pre=["ssh", "-o", "ConnectTimeout=2", MAC_SSH], post=["&& "]),
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print(f"SSH error: {e}")
        print("Mode: Extended Screen")


def switch_to_remote():
    """Mac browser disconnects VNC via WebSocket. Open browser on Linux DP-0."""
    global vncviewer_proc
    # Mac browser receives "remote" via WebSocket and disconnects VNC + goes black
    # Kill any existing remote browser
    #subprocess.run(["killall", "Chrome.app"], capture_output=True)

    import time
    # time.sleep(0.5)
    # Open browser on Linux, will position on DP-0
    env = os.environ.copy()
    env["DISPLAY"] = ":0"
        # "kill", "$(lsof -i udp | grep Brave | cut -d " " -f2)"
    try:
        subprocess.Popen(
            ["ssh", "-o", "ConnectTimeout=5", MAC_SSH,
                """i=0; while [ $i -le 5 ]; do exd=$(lsof -i udp | grep Brave | awk '{print $2}'); if [ -n "$exd" ]; then kill $(echo "$exd" | head -n 1); i=0; fi; sleep 1; i=$((i + 1)); done"""  ],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
    except Exception as e:
        print(f"SSH error: {e}")
    time.sleep(1)
    open_windows = subprocess.check_output(["wmctrl", "-l"], text=True)
    if "Remote Desktop" not in open_windows:
    
        vncviewer_proc = subprocess.Popen(
            get_brave("brave-browser-nightly", REMOTE_URL, post=["--start-fullscreen"]),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            env=env
        )
    # Wait for window, find it by ID, move to DP-0, fullscreen, push behind
    def position_on_dp0():
        import time
        window_name = "Remote Desktop - Brave"
        windows = subprocess.check_output(["wmctrl", "-l"], text=True)
        max_tries = 5
        active_window = None
        while window_name not in windows or max_tries < 1:
            time.sleep(1)
            windows = subprocess.check_output(["wmctrl", "-l"], text=True)
        for window in windows.split("\n")[::-1]:
            print(windows)
            print(window)
            if window_name in window:
                active_window = window.split()[0]
                break
        if not window:
            print("ERROR: Could not find Firefox window")
            return

        if (active_window is None):
            return
        print(active_window, "fdsfsda")
        subprocess.check_output(["xdotool", "windowactivate", active_window], text=True)
        subprocess.check_output(["xdotool", "key", "ctrl+alt+g"], text=True)


        subprocess.check_output(["xdotool", "key", "ctrl+alt+0xff53"], text=True)
        subprocess.check_output(["xdotool", "key", "ctrl+alt+f"], text=True)
        subprocess.check_output(["xdotool", "key", "f11"], text=True)

    position_on_dp0()
    # threading.Thread(target=position_on_dp0, daemon=True).start()
    print("Mode: Remote Desktop (Linux browser on DP-0)")

async def handler(websocket):
    global current_mode
    clients.add(websocket)
    print(f"Client connected ({len(clients)} total)")
    try:
        await websocket.send(json.dumps({"mode": current_mode}))
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data}")
            if "mode" in data and data["mode"] != current_mode:
                current_mode = data["mode"]
                if current_mode == "extended":
                    switch_to_extended()
                elif current_mode == "remote":
                    switch_to_remote()
                # Broadcast to all clients
                for client in clients.copy():
                    try:
                        await client.send(json.dumps({"mode": current_mode}))
                    except:
                        clients.discard(client)
    finally:
        clients.discard(websocket)
        print(f"Client disconnected ({len(clients)} total)")

async def ws_main():
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_ctx.load_cert_chain(CERT, KEY)

    async with websockets.serve(handler, "0.0.0.0", PORT_WS, ssl=ssl_ctx):
        print(f"WSS relay on wss://0.0.0.0:{PORT_WS}")
        async with websockets.serve(handler, "127.0.0.1", PORT_WS_LOCAL):
            print(f"WS relay on ws://127.0.0.1:{PORT_WS_LOCAL}")
            await asyncio.Future()

def serve_http():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = http.server.HTTPServer(("0.0.0.0", PORT_HTTP), http.server.SimpleHTTPRequestHandler)
    print(f"Control panel on http://localhost:{PORT_HTTP}/control.html")
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=serve_http, daemon=True).start()
    asyncio.run(ws_main())
