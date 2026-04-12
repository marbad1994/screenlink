# ScreenLink

**Turn your laptops into extra monitors — and control them all from one desk.**

## The Problem

You've got a Linux desktop, a MacBook, and a Windows laptop. Three machines, three keyboards, three mice. You want one seamless workspace, but every existing solution is either paid, platform-locked, or requires dedicated hardware.

ScreenLink fixes that. Free. Cross-platform. No dongles.

## What It Does

**Screen Extension** — Your MacBook becomes your second monitor. Your Windows laptop becomes your third. Drag windows across all three screens. They behave like real monitors — windows maximize correctly, apps remember their positions, and your compositor treats them as native displays.

**Remote Desktop** — One click and your Linux keyboard and mouse take full control of the Mac or Windows machine. See their actual desktop. Run their apps. Click back and you're in extension mode again.

**Single Keyboard, Single Mouse** — You never touch the laptop keyboards. Everything is driven from your Linux desk.

## How It Works

ScreenLink creates virtual display outputs on the Linux GPU, captures them with TigerVNC, and streams the content to client machines via noVNC over WebSocket. The client is just a browser tab — no app to install.

For remote desktop, the key insight was placing the VNC viewer behind the client's actual OS. Instead of streaming the Mac's screen back through a VNC window — which would create an infinite mirror loop — the VNC session runs fullscreen behind all native macOS windows. What you see is the Mac's real display, rendered natively by macOS, not a compressed stream. Input flows through the VNC connection from the Linux keyboard and mouse. The result is native-quality visuals with zero encoding artifacts.

Mode switching is instant and controlled from a KDE Plasma widget or web panel.

All connections run over TLS on the local network. Authentication is handled automatically.

## Tech

`Xorg` · `NVIDIA virtual outputs` · `x0vncserver` · `noVNC` · `WebSocket/TLS` · `JavaScript` · `Python control server` · `KDE Plasma widget` · `wmctrl` · `mkcert` · `SSH`

## Why It's Different

| | ScreenLink | Duet Display | Luna Display | Sidecar |
|---|---|---|---|---|
| **Price** | Free | $4/mo | $130 | Free |
| **Linux host** | Yes | No | No | No |
| **macOS client** | Yes | Yes | Yes | Yes |
| **Windows client** | Yes | Yes | No | No |
| **Cross-platform** | Any combo | Limited | Mac only | Apple only |
| **Hardware needed** | None | None | Dongle | None |
| **True extension** | Yes | Yes | Yes | Yes |
| **Remote control** | Yes | No | No | No |

## Setup

```bash
./start.sh     # starts everything
./stop.sh      # stops everything
```

Add the KDE widget to your panel for one-click mode switching, or use the web control panel.

## The Xorg Documentation Problem

Getting virtual displays to work meant deep-diving into Xorg configuration — specifically `xorg.conf`, a configuration format that dates back to the early 2000s. The documentation exists, but it's scattered across massive, unformatted PDFs. Hundreds of pages of raw reference material with no search, no examples, no modern structure. Stack Overflow answers are sparse and often outdated. The community has largely moved on to Wayland, leaving X11 configuration knowledge in a slowly decaying archive.

After spending days cross-referencing PDFs, man pages, and mailing list threads just to understand how `ConnectedMonitor` interacts with `ModeValidation` and `MetaModes`, I decided to solve this for good. I built a modern, searchable documentation site — indexed, formatted, and organized by topic — so that the next time I (or anyone) needs to configure NVIDIA virtual outputs, dual GPU setups, or custom modelines, the answer is a search query away instead of buried on page 347 of a PDF.
