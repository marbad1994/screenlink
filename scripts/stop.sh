#!/bin/bash
# Stop the Screen Extender system

echo "Stopping Screen Extender..."

pkill -f x0vncserver 2>/dev/null
pkill -f "novnc_proxy" 2>/dev/null
pkill -f "python.*8080" 2>/dev/null
pkill -f "control.py" 2>/dev/null
pkill -9 -f remote-desktop-profile
ssh marcusbader@192.168.50.22 "pkill -9 -f extend-screen-profile"
echo "Stopped."
