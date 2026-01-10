#!/bin/bash

UUID="sticky-timer@stup"
SCRIPT_PATH=$(dirname "$(readlink -f "$0")")
SOURCE_DIR="$SCRIPT_PATH/$UUID"
DEST_DIR="$HOME/.local/share/gnome-shell/extensions/$UUID"

echo "🚀 Installing Permanent Sticky Timer GNOME Extension..."

# 1. Check if the user is actually on GNOME
if [ "$XDG_CURRENT_DESKTOP" != "GNOME" ]; then
    echo "❌ Error: This extension only works on the GNOME Desktop Environment."
    exit 1
fi

# 2. Check for the gnome-extensions CLI tool
if ! command -v gnome-extensions &> /dev/null; then
    echo "📦 GNOME tools missing. Attempting to install..."
    sudo apt update && sudo apt install -y gnome-shell-extension-manager gnome-browser-connector
fi

# 3. Verify the source folder exists next to this script
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Error: Could not find the folder '$UUID' at $SOURCE_DIR"
    echo "Please ensure the extension folder is in the same directory as this script."
    exit 1
fi

# 4. Create the extensions directory and copy files
mkdir -p "$HOME/.local/share/gnome-shell/extensions"
if [ -d "$DEST_DIR" ]; then
    rm -rf "$DEST_DIR"
fi

cp -r "$SOURCE_DIR" "$DEST_DIR"

# 5. Enable the Master Switch and the Extension
echo "🔧 Configuring GNOME Shell..."
gsettings set org.gnome.shell disable-user-extensions false
gnome-extensions enable "$UUID"

echo "-------------------------------------------------------"
echo "✅ Installation Complete!"
echo "⚠️  IMPORTANT: You must RESTART GNOME for the extension to load."
echo "   - On X11: Press Alt+F2, type 'r', and hit Enter."
echo "   - On Wayland (Ubuntu 24.04+): Log out and log back in."
echo "-------------------------------------------------------"