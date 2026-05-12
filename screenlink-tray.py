#!/usr/bin/env python3
"""
ScreenLink XFCE System Tray Widget
Replicates the KDE Plasmoid in GTK3 for XFCE.
Requires: python-gobject, libappindicator-gtk3, python-websocket-client
Install: sudo pacman -S python-gobject libappindicator-gtk3 python-websocket-client
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GLib, Gdk, Pango
from gi.repository import AppIndicator3 as AppIndicator

import threading
import json
import subprocess
import websocket
import time

# ── Config ─────────────────────────────────────────────────────────────────
WS_URL      = "ws://localhost:8085"
PROJECT_DIR = "/home/marcus/Documents/repos/local-remote-workspace"

HOST = {
    "device":     "Desktop PC",
    "os":         "Linux",
    "screen":     "1920×1080",
    "connection": "Ethernet",
    "ip":         "192.168.50.181",
}
CLIENT = {
    "device":     "MacBook Air",
    "os":         "macOS",
    "screen":     "1440×900",
    "connection": "WiFi",
    "ip":         "192.168.50.22",
}

# ── Colors ──────────────────────────────────────────────────────────────────
CSS = b"""
window.sl-popup {
    background-color: #1a1d23;
    border-width: 1px;
    border-style: solid;
    border-color: #2e3340;
    border-radius: 10px;
}
.sl-header {
    background-color: #1f2330;
    border-bottom-width: 1px;
    border-bottom-style: solid;
    border-bottom-color: #2e3340;
    border-radius: 10px 10px 0 0;
    padding: 10px 14px;
}
.sl-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    font-weight: 700;
    color: #e2e8f0;
    letter-spacing: 1px;
}
.sl-section-label {
    font-size: 10px;
    font-weight: 600;
    color: #4a5568;
    letter-spacing: 1.5px;
    padding: 8px 14px 2px 14px;
}
.sl-card {
    background-color: #222635;
    border-radius: 8px;
    margin: 4px 10px;
    padding: 10px 12px;
}
.sl-device-name {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    color: #e2e8f0;
}
.sl-device-sub {
    font-size: 10px;
    color: #4a5568;
    margin-top: 1px;
}
.sl-detail-key {
    font-size: 10px;
    color: #4a5568;
    min-width: 80px;
}
.sl-detail-val {
    font-size: 10px;
    color: #94a3b8;
    font-family: 'IBM Plex Mono', monospace;
}
.sl-dot-green {
    color: #22c55e;
    font-size: 18px;
}
.sl-dot-red {
    color: #ef4444;
    font-size: 18px;
}
.sl-mode-btn {
    background-color: #2d3348;
    border-width: 1px;
    border-style: solid;
    border-color: #3d4460;
    border-radius: 6px;
    color: #94a3b8;
    font-size: 10px;
    font-family: 'IBM Plex Mono', monospace;
    padding: 4px 10px;
}
.sl-mode-btn:hover {
    background-color: #3d4460;
    color: #e2e8f0;
    border-color: #5a6480;
}
.sl-footer {
    background-color: #1f2330;
    border-top-width: 1px;
    border-top-style: solid;
    border-top-color: #2e3340;
    border-radius: 0 0 10px 10px;
    padding: 6px 10px;
}
.sl-ctrl-btn {
    background-color: transparent;
    border-width: 1px;
    border-style: solid;
    border-color: #2e3340;
    border-radius: 5px;
    color: #64748b;
    font-size: 10px;
    padding: 3px 10px;
    min-width: 50px;
}
.sl-ctrl-btn:hover {
    background-color: #2e3340;
    color: #94a3b8;
}
.sl-ctrl-btn.start:hover { border-color: #22c55e; color: #22c55e; }
.sl-ctrl-btn.stop:hover  { border-color: #ef4444; color: #ef4444; }
.sl-logs-btn {
    background-color: transparent;
    border-width: 0;
    color: #4a5568;
    font-size: 10px;
    padding: 3px 6px;
}
.sl-logs-btn:hover { color: #94a3b8; }
.sl-expand-btn {
    background-color: transparent;
    border-width: 0;
    color: #4a5568;
    font-size: 11px;
    padding: 0 4px;
    min-width: 0;
}
.sl-expand-btn:hover { color: #94a3b8; }
.sl-offline {
    opacity: 0.4;
}
.sl-separator {
    background-color: #2e3340;
    min-height: 1px;
    margin: 4px 0;
}
.sl-mode-badge {
    font-size: 10px;
    font-family: 'IBM Plex Mono', monospace;
    border-radius: 4px;
    padding: 1px 7px;
    background-color: #1a3a2a;
    color: #22c55e;
    border-width: 1px;
    border-style: solid;
    border-color: #226644;
}
.sl-mode-badge.remote {
    background-color: #2a1a3a;
    color: #a78bfa;
    border-color: #7744aa;
}
"""

class ScreenLinkWidget:
    def __init__(self):
        self.ws_connected = False
        self.current_mode = "extended"
        self.ws = None
        self.popup = None
        self.host_expanded = False
        self.client_expanded = False

        # Apply CSS
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Tray indicator
        self.indicator = AppIndicator.Indicator.new(
            "screenlink", "video-display",
            AppIndicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)

        # Minimal tray menu (just to satisfy AppIndicator requirement)
        menu = Gtk.Menu()
        open_item = Gtk.MenuItem(label="Open ScreenLink")
        open_item.connect("activate", self.toggle_popup)
        menu.append(open_item)
        sep = Gtk.SeparatorMenuItem()
        menu.append(sep)
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", Gtk.main_quit)
        menu.append(quit_item)
        menu.show_all()
        self.indicator.set_menu(menu)
        self.indicator.connect("scroll-event", self.on_scroll)

        self._build_popup()
        self._start_ws()

    # ── WebSocket ────────────────────────────────────────────────────────────
    def _start_ws(self):
        t = threading.Thread(target=self._ws_loop, daemon=True)
        t.start()

    def _ws_loop(self):
        while True:
            try:
                self.ws = websocket.WebSocketApp(
                    WS_URL,
                    on_open=self._on_ws_open,
                    on_message=self._on_ws_message,
                    on_close=self._on_ws_close,
                    on_error=self._on_ws_error,
                )
                self.ws.run_forever()
            except Exception:
                pass
            GLib.idle_add(self._set_connected, False)
            time.sleep(5)

    def _on_ws_open(self, ws):
        GLib.idle_add(self._set_connected, True)

    def _on_ws_message(self, ws, message):
        try:
            data = json.loads(message)
            if "mode" in data:
                GLib.idle_add(self._set_mode, data["mode"])
        except Exception:
            pass

    def _on_ws_close(self, ws, *args):
        GLib.idle_add(self._set_connected, False)

    def _on_ws_error(self, ws, *args):
        GLib.idle_add(self._set_connected, False)

    def _set_connected(self, connected):
        self.ws_connected = connected
        self._refresh_popup()
        self.indicator.set_icon("video-display" if connected else "video-display-symbolic")

    def _set_mode(self, mode):
        self.current_mode = mode
        self._refresh_popup()

    def send_mode(self, mode):
        if self.ws and self.ws_connected:
            try:
                self.ws.send(json.dumps({"mode": mode}))
            except Exception:
                pass

    def reconnect(self):
        if self.ws:
            try: self.ws.close()
            except Exception: pass

    # ── Shell commands ───────────────────────────────────────────────────────
    def run_cmd(self, cmd):
        subprocess.Popen(cmd, shell=True)

    # ── Popup window ─────────────────────────────────────────────────────────
    def _build_popup(self):
        self.popup = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.popup.get_style_context().add_class("sl-popup")
        self.popup.set_decorated(False)
        self.popup.set_resizable(False)
        self.popup.set_keep_above(True)
        self.popup.set_skip_taskbar_hint(True)
        self.popup.set_skip_pager_hint(True)
        self.popup.set_default_size(300, -1)
        self.popup.connect("focus-out-event", lambda w, e: w.hide())

        self.popup_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.popup.add(self.popup_box)
        self._refresh_popup()

    def _refresh_popup(self):
        # Clear
        for child in self.popup_box.get_children():
            self.popup_box.remove(child)

        # ── Header ──────────────────────────────────────────────────────────
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header.get_style_context().add_class("sl-header")

        title = Gtk.Label(label="SCREENLINK")
        title.get_style_context().add_class("sl-title")
        title.set_halign(Gtk.Align.START)
        header.pack_start(title, True, True, 0)

        logs_btn = Gtk.Button(label="⬛ logs")
        logs_btn.get_style_context().add_class("sl-logs-btn")
        logs_btn.connect("clicked", lambda b: self.run_cmd("xterm -e 'tail -f /tmp/screenlink.log'"))
        header.pack_end(logs_btn, False, False, 0)
        self.popup_box.pack_start(header, False, False, 0)

        # ── Host section ────────────────────────────────────────────────────
        host_label = Gtk.Label(label="HOST")
        host_label.get_style_context().add_class("sl-section-label")
        host_label.set_halign(Gtk.Align.START)
        self.popup_box.pack_start(host_label, False, False, 0)

        host_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        host_card.get_style_context().add_class("sl-card")

        host_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        dot = Gtk.Label(label="●")
        dot.get_style_context().add_class("sl-dot-green" if self.ws_connected else "sl-dot-red")
        host_row.pack_start(dot, False, False, 0)

        host_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        name_lbl = Gtk.Label(label=HOST["device"])
        name_lbl.get_style_context().add_class("sl-device-name")
        name_lbl.set_halign(Gtk.Align.START)
        sub_lbl = Gtk.Label(label=f"{HOST['os']}  ·  {HOST['screen']}  ·  {HOST['connection']}")
        sub_lbl.get_style_context().add_class("sl-device-sub")
        sub_lbl.set_halign(Gtk.Align.START)
        host_info.pack_start(name_lbl, False, False, 0)
        host_info.pack_start(sub_lbl, False, False, 0)
        host_row.pack_start(host_info, True, True, 0)

        expand_host = Gtk.Button(label="▾" if self.host_expanded else "▸")
        expand_host.get_style_context().add_class("sl-expand-btn")
        expand_host.connect("clicked", self._toggle_host_expand)
        host_row.pack_end(expand_host, False, False, 0)

        host_card.pack_start(host_row, False, False, 0)

        if self.host_expanded:
            host_card.pack_start(self._detail_grid(HOST), False, False, 4)

        self.popup_box.pack_start(host_card, False, False, 0)

        # ── Separator ───────────────────────────────────────────────────────
        sep = Gtk.Separator()
        sep.get_style_context().add_class("sl-separator")
        self.popup_box.pack_start(sep, False, False, 4)

        # ── Client section ──────────────────────────────────────────────────
        conn_label = Gtk.Label(label="CONNECTED" if self.ws_connected else "DISCONNECTED")
        conn_label.get_style_context().add_class("sl-section-label")
        conn_label.set_halign(Gtk.Align.START)
        self.popup_box.pack_start(conn_label, False, False, 0)

        client_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        client_card.get_style_context().add_class("sl-card")

        client_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        laptop_icon = Gtk.Label(label="💻")
        if not self.ws_connected:
            laptop_icon.get_style_context().add_class("sl-offline")
        client_row.pack_start(laptop_icon, False, False, 0)

        client_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        if self.ws_connected:
            mode_text = "Extended Screen" if self.current_mode == "extended" else "Remote Desktop"
            c_name = Gtk.Label(label=mode_text)
            c_name.get_style_context().add_class("sl-device-name")
            c_name.set_halign(Gtk.Align.START)
            c_sub_text = f"{CLIENT['device']}  ·  {CLIENT['screen']}" if self.current_mode == "extended" else CLIENT["device"]
            c_sub = Gtk.Label(label=c_sub_text)
            c_sub.get_style_context().add_class("sl-device-sub")
            c_sub.set_halign(Gtk.Align.START)
        else:
            c_name = Gtk.Label(label=CLIENT["device"])
            c_name.get_style_context().add_class("sl-device-name")
            c_name.get_style_context().add_class("sl-offline")
            c_name.set_halign(Gtk.Align.START)
            c_sub = Gtk.Label(label="Service not running")
            c_sub.get_style_context().add_class("sl-device-sub")
            c_sub.set_halign(Gtk.Align.START)

        client_info.pack_start(c_name, False, False, 0)
        client_info.pack_start(c_sub, False, False, 0)
        client_row.pack_start(client_info, True, True, 0)

        if self.ws_connected:
            next_mode = "remote" if self.current_mode == "extended" else "extended"
            btn_label = "→ Remote" if self.current_mode == "extended" else "→ Extend"
            mode_btn = Gtk.Button(label=btn_label)
            mode_btn.get_style_context().add_class("sl-mode-btn")
            mode_btn.connect("clicked", lambda b: self.send_mode(next_mode))
            client_row.pack_end(mode_btn, False, False, 0)

            expand_client = Gtk.Button(label="▾" if self.client_expanded else "▸")
            expand_client.get_style_context().add_class("sl-expand-btn")
            expand_client.connect("clicked", self._toggle_client_expand)
            client_row.pack_end(expand_client, False, False, 0)
        else:
            reconnect_btn = Gtk.Button(label="↻")
            reconnect_btn.get_style_context().add_class("sl-expand-btn")
            reconnect_btn.connect("clicked", lambda b: self.reconnect())
            client_row.pack_end(reconnect_btn, False, False, 0)

        client_card.pack_start(client_row, False, False, 0)

        if self.client_expanded and self.ws_connected:
            client_card.pack_start(self._detail_grid(CLIENT), False, False, 4)

        self.popup_box.pack_start(client_card, False, False, 0)

        # ── Footer ───────────────────────────────────────────────────────────
        sep2 = Gtk.Separator()
        sep2.get_style_context().add_class("sl-separator")
        self.popup_box.pack_start(sep2, False, False, 4)

        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        footer.get_style_context().add_class("sl-footer")

        for label, cmd_arg, extra_class in [
            ("▶ Start",   "start",   "start"),
            ("■ Stop",    "stop",    "stop"),
            ("↻ Restart", "restart", ""),
        ]:
            btn = Gtk.Button(label=label)
            btn.get_style_context().add_class("sl-ctrl-btn")
            if extra_class:
                btn.get_style_context().add_class(extra_class)
            btn.connect("clicked", lambda b, a=cmd_arg: self.run_cmd(f"{PROJECT_DIR}/ctl.sh {a}"))
            footer.pack_start(btn, True, True, 0)

        self.popup_box.pack_start(footer, False, False, 0)
        self.popup_box.show_all()

    def _detail_grid(self, info):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        box.set_margin_top(8)
        box.set_margin_start(10)
        keys = [k for k in info.keys()]
        for k in keys:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            key_lbl = Gtk.Label(label=k.upper())
            key_lbl.get_style_context().add_class("sl-detail-key")
            key_lbl.set_halign(Gtk.Align.START)
            val_lbl = Gtk.Label(label=info[k])
            val_lbl.get_style_context().add_class("sl-detail-val")
            val_lbl.set_halign(Gtk.Align.START)
            row.pack_start(key_lbl, False, False, 0)
            row.pack_start(val_lbl, False, False, 0)
            box.pack_start(row, False, False, 0)
        return box

    def _toggle_host_expand(self, btn):
        self.host_expanded = not self.host_expanded
        self._refresh_popup()
        if self.popup.get_visible():
            self.popup.resize(300, 1)

    def _toggle_client_expand(self, btn):
        self.client_expanded = not self.client_expanded
        self._refresh_popup()
        if self.popup.get_visible():
            self.popup.resize(300, 1)

    # ── Tray interaction ─────────────────────────────────────────────────────
    def on_scroll(self, indicator, steps, direction):
        self.toggle_popup()

    def toggle_popup(self, *args):
        if self.popup.get_visible():
            self.popup.hide()
        else:
            self._refresh_popup()
            self.popup.show_all()
            display = Gdk.Display.get_default()
            monitor = display.get_primary_monitor() or display.get_monitor(0)
            geo = monitor.get_geometry()
            self.popup.resize(300, 1)
            pw, ph = self.popup.get_size()
            x = geo.x + geo.width - pw - 10
            y = geo.y + geo.height - ph - 48
            self.popup.move(x, y)
            self.popup.present()


if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = ScreenLinkWidget()
    Gtk.main()
