#!/usr/bin/env bash
# RoseStrap uninstaller
# Removes everything install.sh created. Does NOT touch Sober or Roblox
# itself, since those are separate apps you may still want to keep.

set -e

INSTALL_DIR="$HOME/.local/share/rosestrap"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
CONFIG_DIR="$HOME/.config/rosestrap"

echo "=================================="
echo "   RoseStrap Uninstaller"
echo "=================================="
echo

read -p "This will remove RoseStrap and its settings. Continue? [y/N] " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# --- 1. Remove launcher command ----------------------------------------------
if [ -f "$BIN_DIR/rosestrap" ]; then
    rm -f "$BIN_DIR/rosestrap"
    echo "[ok] Removed $BIN_DIR/rosestrap"
fi

# --- 2. Remove desktop entry ---------------------------------------------------
if [ -f "$DESKTOP_DIR/rosestrap.desktop" ]; then
    rm -f "$DESKTOP_DIR/rosestrap.desktop"
    echo "[ok] Removed desktop entry"
fi

# --- 3. Remove icons -------------------------------------------------------------
rm -f "$HOME/.local/share/pixmaps/rosestrap.png"
rm -f "$HOME/.local/share/icons/hicolor/64x64/apps/rosestrap.png"
rm -f "$HOME/.local/share/icons/hicolor/128x128/apps/rosestrap.png"
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
fi
echo "[ok] Removed icons"

# --- 4. Ask about mods (they live inside INSTALL_DIR too) ----------------------
KEEP_MODS=""
if [ -d "$INSTALL_DIR/Mods" ] && [ -n "$(ls -A "$INSTALL_DIR/Mods" 2>/dev/null)" ]; then
    read -p "Keep your imported mods (found in $INSTALL_DIR/Mods)? [Y/n] " keep
    if [[ ! "$keep" =~ ^[Nn]$ ]]; then
        KEEP_MODS="yes"
    fi
fi

if [ -d "$INSTALL_DIR" ]; then
    if [ -n "$KEEP_MODS" ]; then
        BACKUP_DIR="$HOME/rosestrap-mods-backup"
        mkdir -p "$BACKUP_DIR"
        cp -r "$INSTALL_DIR/Mods/." "$BACKUP_DIR/" 2>/dev/null || true
        echo "[ok] Backed up mods to $BACKUP_DIR"
    fi
    rm -rf "$INSTALL_DIR"
    echo "[ok] Removed $INSTALL_DIR"
fi

# --- 5. Remove config -------------------------------------------------------------
if [ -d "$CONFIG_DIR" ]; then
    rm -rf "$CONFIG_DIR"
    echo "[ok] Removed $CONFIG_DIR"
fi

echo
echo "=================================="
echo " RoseStrap has been uninstalled."
echo "=================================="
echo
echo "Note: Sober (the Roblox compatibility layer) and its Flatpak data"
echo "were left untouched. To remove Sober as well, run:"
echo "  flatpak uninstall org.vinegarhq.Sober"
