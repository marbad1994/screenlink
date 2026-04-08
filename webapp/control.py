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
BASE_URL = "https://192.168.50.181:8080"
REMOTE_URL = BASE_URL + "/remote.html"

clients = set()
current_mode = "extended"
vncviewer_proc = None
EXTEND_PROFILE = "extend-screen-profile"
REMOTE_PROFILE = "remote-desktop-profile"

open_browser_data = {
    EXTEND_PROFILE: {
        "firefox":{
            "mac": ["/Applications/Firefox.app/Contents/MacOS/firefox"]
        },
        "flags": ["--new-window", "-P", f"{EXTEND_PROFILE}", "--kiosk"],
        "url": [BASE_URL]
    },
    REMOTE_PROFILE: {
        "firefox":{
            "linux": ["firefox"]
        },
        "flags": ["--new-window", "-P", f"{REMOTE_PROFILE}"],
        "url": [REMOTE_URL]
    }
}

def get_ssh_cmd(ssh):
    return ["ssh", "-o", "ConnectTimeout=5", ssh]

def get_brave(brave, url, profile, pre=[], post=[]):
    command = f"{brave}"
    return_string = command + url
    return pre + return_string.split(" ") + post

def get_open_browser_cmd(role, os):
    o = open_browser_data[role]
    firefox = o.get("firefox", {}).get(os, [])
    flags = o.get("flags", [])
    url = o.get("url", [])
    browser_command =  firefox + flags + url
    return browser_command

def kill_browser(role):
    kill_command = ["pkill", "-9", "-f", role]
    return kill_command


subprocess.Popen(
    get_ssh_cmd(MAC_SSH) + get_open_browser_cmd(EXTEND_PROFILE, "mac"),
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)

def clean_up():
    try:
        subprocess.run(kill_browser(REMOTE_PROFILE), text=True)
        subprocess.Popen(
            get_ssh_cmd(MAC_SSH) + kill_browser(REMOTE_PROFILE),
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
    except Exception as e:
        print(f"SSH error: {e}")

def switch_to_extended():
    """Close Linux remote browser, open fresh Chrome on Mac."""
    # subprocess.run(["killall", "brave"], capture_output=True)
    clean_up()
    # Open fresh Chrome on Mac with the extended screen page
    open_windows = subprocess.check_output(["wmctrl", "-l"], text=True)
    if EXTEND_PROFILE not in open_windows:
        try:
            subprocess.Popen(
                # get_brave("/Applications/Brave\ Browser\ Beta.app/Contents/MacOS/Brave\ Browser\ Beta", "https://192.168.50.181:8080/  --args --start-fullscreen", pre=["ssh", "-o", "ConnectTimeout=2", MAC_SSH], post=["&& "]),
                get_ssh_cmd(MAC_SSH) + get_open_browser_cmd(EXTEND_PROFILE, "mac"),
                # get_brave(" --new-window --kiosk ", "https://192.168.50.181:8080/ &", pre=["ssh", "-o", "ConnectTimeout=2", MAC_SSH]),
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

        # "kill", "$(lsof -i udp | grep Brave | cut -d " " -f2)"

    def position_on_dp0(n=0):
        import time
        clean_up()
        subprocess.Popen(
            get_open_browser_cmd(REMOTE_PROFILE, "linux")
        )
        time.sleep(2)
        
        windows = subprocess.check_output(["wmctrl", "-l"], text=True)
        max_tries = 100
        active_window = None
        while REMOTE_PROFILE not in windows and max_tries > 1:
            time.sleep(0.5)
            windows = subprocess.check_output(["wmctrl", "-l"], text=True)
            max_tries -= 1
        active_window = [window for window in windows.split("\n") if REMOTE_PROFILE in window][0]

        if active_window is None:
            if n == 1:
                return
            position_on_dp0(n=1)
            return
        subprocess.run(["xdotool", "windowactivate", active_window])
        time.sleep(2)
        subprocess.run(["xdotool", "key", "ctrl+alt+g"])
        subprocess.run(["xdotool", "key", "ctrl+alt+0xff53"])
        subprocess.run(["xdotool", "key", "ctrl+alt+f"])
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
