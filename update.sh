#!/usr/bin/env bash
# RoseStrap updater
# Pulls the latest code (if this is a git checkout) and refreshes the
# installed copy in ~/.local/share/rosestrap without re-checking system
# dependencies (flatpak, tkinter, Sober) every time.

set -e

INSTALL_DIR="$HOME/.local/share/rosestrap"
REPO_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=================================="
echo "   RoseStrap Updater"
echo "=================================="
echo

if [ ! -d "$INSTALL_DIR" ]; then
    echo "RoseStrap doesn't look installed yet ($INSTALL_DIR not found)."
    echo "Run ./install.sh first."
    exit 1
fi

# --- 1. Pull latest source if this folder is a git repo ---------------------
if [ -d "$REPO_SRC/.git" ]; then
    echo "[..] Pulling latest changes from git..."
    git -C "$REPO_SRC" pull --ff-only
else
    echo "[!] Not a git checkout, skipping git pull."
    echo "    (Download/extract the latest release into this folder first if needed.)"
fi

# --- 2. Re-sync app files into the install directory ------------------------
echo "[..] Updating installed files in $INSTALL_DIR..."
rsync -a --exclude '__pycache__' --exclude '.git' --exclude 'install.sh' --exclude 'update.sh' \
    "$REPO_SRC"/ "$INSTALL_DIR"/ 2>/dev/null || \
    cp -r "$REPO_SRC"/* "$INSTALL_DIR"/

# --- 3. Refresh icon in case it changed --------------------------------------
SRC_ICON=""
if [ -f "$INSTALL_DIR/rosestrap_logo_76.png" ]; then
    SRC_ICON="$INSTALL_DIR/rosestrap_logo_76.png"
elif [ -f "$INSTALL_DIR/rosestrap_logo_30.png" ]; then
    SRC_ICON="$INSTALL_DIR/rosestrap_logo_30.png"
fi

if [ -n "$SRC_ICON" ]; then
    mkdir -p "$HOME/.local/share/pixmaps" \
             "$HOME/.local/share/icons/hicolor/64x64/apps" \
             "$HOME/.local/share/icons/hicolor/128x128/apps"
    cp "$SRC_ICON" "$HOME/.local/share/pixmaps/rosestrap.png"
    cp "$SRC_ICON" "$HOME/.local/share/icons/hicolor/64x64/apps/rosestrap.png"
    cp "$SRC_ICON" "$HOME/.local/share/icons/hicolor/128x128/apps/rosestrap.png"
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
    fi
fi

echo
echo "=================================="
echo " RoseStrap updated successfully!"
echo "=================================="
