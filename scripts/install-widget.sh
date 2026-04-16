#!/bin/bash
# Install the Screen Extender KDE Plasma widget

PLASMOID_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/plasmoid"

echo "Installing Screen Extender widget..."

# Remove old version if exists
kpackagetool6 -r com.screenextender.control -t Plasma/Applet 2>/dev/null || true

# Install
kpackagetool6 -i "$PLASMOID_DIR" -t Plasma/Applet

echo ""
echo "Done! Right-click your KDE panel → Add Widgets → search 'Screen Extender'"
echo "Or right-click desktop → Add Widgets"
