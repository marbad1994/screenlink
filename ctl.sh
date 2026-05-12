#!/bin/bash
# Non-blocking controller for the widget
# Usage: ctl.sh start|stop|restart

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$1" in
    start)
        nohup bash "$PROJECT_DIR/start.sh" > /tmp/screenlink.log 2>&1 &
        disown
        echo "Started (PID $!)"
        ;;
    stop)
        bash "$PROJECT_DIR/stop.sh"
        echo "Stopped"
        ;;
    restart)
        bash "$PROJECT_DIR/stop.sh"
        sleep 2
        nohup bash "$PROJECT_DIR/start.sh" > /tmp/screenlink.log 2>&1 &
        disown
        echo "Restarted (PID $!)"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac
