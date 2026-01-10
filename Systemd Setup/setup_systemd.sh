#!/bin/bash

# Define paths
SYSTEMD_DIR="$HOME/.config/systemd/user"
mkdir -p "$SYSTEMD_DIR"

echo "⚙️ Setting up Systemd Watchdog..."

# 1. Create the main watchdog service
cat <<EOF > "$SYSTEMD_DIR/watchdog.service"
[Unit]
Description=Sticky Timer
After=graphical.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 %h/Permanent_sticky_timer/sticky_timer.py
Restart=always
RestartSec=2
Environment=DISPLAY=:0
Environment=WAYLAND_DISPLAY=%t
Environment=XDG_RUNTIME_DIR=%t

[Install]
WantedBy=default.target
EOF

# 2. Create the monitor service (Oneshot)
cat <<EOF > "$SYSTEMD_DIR/watchdog_monitor.service"
[Unit]
Description=Monitor for watchdog.service and restart if needed

[Service]
Type=oneshot
ExecStart=/bin/sh -c "systemctl --user is-active --quiet watchdog.service || systemctl --user start watchdog.service"
EOF

# 3. Create the timer
cat <<EOF > "$SYSTEMD_DIR/watchdog_monitor.timer"
[Unit]
Description=Run watchdog_monitor.service every 30 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=30min
Unit=watchdog_monitor.service

[Install]
WantedBy=timers.target
EOF

# 4. Reload and Enable
systemctl --user daemon-reload
systemctl --user enable watchdog.service
systemctl --user enable watchdog_monitor.timer
systemctl --user start watchdog.service
systemctl --user start watchdog_monitor.timer

echo "✅ Systemd services installed and started!"