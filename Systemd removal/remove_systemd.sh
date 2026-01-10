#!/bin/bash
# uninstall_watchdog.sh - Completely removes the Sticky Timer watchdog system

SYSTEMD_DIR="$HOME/.config/systemd/user"
UNITS=("watchdog.service" "watchdog_monitor.service" "watchdog_monitor.timer")

echo "🧹 Starting the cleanup process..."

# 1. Stop and Disable the units
for unit in "${UNITS[@]}"; do
    if systemctl --user is-active --quiet "$unit" || systemctl --user is-enabled --quiet "$unit"; then
        echo "Stopping and disabling $unit..."
        systemctl --user stop "$unit" 2>/dev/null
        systemctl --user disable "$unit" 2>/dev/null
    fi
done

# 2. Remove the actual files
echo "Deleting systemd unit files..."
for unit in "${UNITS[@]}"; do
    rm -f "$SYSTEMD_DIR/$unit"
done

# 3. Reload systemd to apply changes
systemctl --user daemon-reload
systemctl --user reset-failed

echo "-------------------------------------------------------"
echo "✅ Cleanup Complete! The ghost has been exorcised."
echo "-------------------------------------------------------"