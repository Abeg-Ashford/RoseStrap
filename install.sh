#!/usr/bin/env bash
# RoseStrap installer
# A modern, open-source Roblox launcher for Linux (Bloxstrap-inspired)

set -e

INSTALL_DIR="$HOME/.local/share/rosestrap"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/76x76/apps"
SOBER_APP_ID="org.vinegarhq.Sober"
REPO_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=================================="
echo "   RoseStrap Installer"
echo "=================================="
echo

# --- Detect package manager -------------------------------------------------
PKG_MANAGER=""
if command -v apt >/dev/null 2>&1; then
    PKG_MANAGER="apt"
elif command -v dnf >/dev/null 2>&1; then
    PKG_MANAGER="dnf"
elif command -v pacman >/dev/null 2>&1; then
    PKG_MANAGER="pacman"
elif command -v zypper >/dev/null 2>&1; then
    PKG_MANAGER="zypper"
fi

# --- 1. Check Python 3 -------------------------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is not installed. Please install Python 3 first."
    exit 1
fi
echo "[ok] Found $(python3 --version)"

# --- 2. Check / install tkinter ----------------------------------------------
if ! python3 -c "import tkinter" >/dev/null 2>&1; then
    echo "[!] tkinter not found, attempting to install..."
    case "$PKG_MANAGER" in
        apt)    sudo apt update && sudo apt install -y python3-tk ;;
        dnf)    sudo dnf install -y python3-tkinter ;;
        pacman) sudo pacman -S --noconfirm tk ;;
        zypper) sudo zypper install -y python3-tk ;;
        *)
            echo "Could not detect package manager. Please install the 'tkinter' package for your distro manually."
            exit 1
            ;;
    esac
else
    echo "[ok] tkinter is available"
fi

# --- 3. Check / install flatpak ----------------------------------------------
if ! command -v flatpak >/dev/null 2>&1; then
    echo "[!] flatpak not found, attempting to install..."
    case "$PKG_MANAGER" in
        apt)    sudo apt update && sudo apt install -y flatpak ;;
        dnf)    sudo dnf install -y flatpak ;;
        pacman) sudo pacman -S --noconfirm flatpak ;;
        zypper) sudo zypper install -y flatpak ;;
        *)
            echo "Could not detect package manager. Please install 'flatpak' for your distro manually."
            exit 1
            ;;
    esac
else
    echo "[ok] flatpak is available"
fi

# Make sure flathub remote exists
if ! flatpak remote-list 2>/dev/null | grep -q flathub; then
    echo "[!] Adding Flathub remote..."
    flatpak remote-add --if-not-exists --user flathub https://flathub.org/repo/flathub.flatpakrepo
fi

# --- 4. Check / install Sober -------------------------------------------------
if ! flatpak list 2>/dev/null | grep -q "$SOBER_APP_ID"; then
    echo "[!] Sober (Roblox compatibility layer) not found, installing..."
    flatpak install --user -y flathub "$SOBER_APP_ID"
else
    echo "[ok] Sober is already installed"
fi

# --- 5. Copy app files --------------------------------------------------------
echo "[..] Installing RoseStrap to $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
rsync -a --exclude '__pycache__' --exclude 'install.sh' "$REPO_SRC"/ "$INSTALL_DIR"/ 2>/dev/null || \
    cp -r "$REPO_SRC"/* "$INSTALL_DIR"/

# --- 6. Create launcher script -------------------------------------------------
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/rosestrap" <<EOF
#!/usr/bin/env bash
cd "$INSTALL_DIR"
exec python3 main.py "\$@"
EOF
chmod +x "$BIN_DIR/rosestrap"

# --- 7. Create desktop entry ----------------------------------------------------
mkdir -p "$DESKTOP_DIR" "$ICON_DIR"
if [ -f "$INSTALL_DIR/rosestrap_logo_76.png" ]; then
    cp "$INSTALL_DIR/rosestrap_logo_76.png" "$ICON_DIR/rosestrap.png"
fi

cat > "$DESKTOP_DIR/rosestrap.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=RoseStrap
Comment=A modern, open-source Roblox launcher for Linux
Exec=$BIN_DIR/rosestrap
Icon=rosestrap
Terminal=false
Categories=Game;
EOF

update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true

# --- 8. PATH check ---------------------------------------------------------------
echo
echo "=================================="
echo " Installation complete!"
echo "=================================="
echo
if ! echo "$PATH" | tr ':' '\n' | grep -qx "$BIN_DIR"; then
    echo "Note: $BIN_DIR is not in your PATH."
    echo "Add this to your ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo
fi
echo "You can now launch RoseStrap by:"
echo "  - Running 'rosestrap' in a terminal"
echo "  - Finding 'RoseStrap' in your applications menu"
echo
