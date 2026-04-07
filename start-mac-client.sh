#!/bin/bash
# Run this ON the Mac, or trigger via SSH from Linux:
#   ssh marcusbader@192.168.50.22 'bash ~/start-mac-client.sh'

LINUX_IP="192.168.50.181"

# Open Chrome in kiosk (true fullscreen) mode
open -a "Google Chrome" --args \
    --kiosk \
    --ignore-certificate-errors \
    --autoplay-policy=no-user-gesture-required \
    "https://${LINUX_IP}:8080/"
