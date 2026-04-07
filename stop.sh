#!/bin/bash
# Stop the Screen Extender system

echo "Stopping Screen Extender..."

pkill -f x0vncserver 2>/dev/null
pkill -f "novnc_proxy" 2>/dev/null
pkill -f "python.*8080" 2>/dev/null
pkill -f "control.py" 2>/dev/null

echo "Stopped."
