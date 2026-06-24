#!/bin/bash
# EduOS System Settings Branding Installer
# Applies the EduOS Liquid Glass theme to KDE System Settings

set -e

COLOR_DIR="$HOME/.local/share/color-schemes"
PLASMA_THEME_DIR="$HOME/.local/share/plasma/desktoptheme"
SDDM_THEME_DIR="$HOME/.local/share/sddm/themes"
SPLASH_DIR="$HOME/.local/share/plasma/splash"

THEMES_SRC="$(cd "$(dirname "$0")/.." && pwd)"

echo "◆ EduOS Theme Installer"
echo "======================="
echo ""

# 1. Color scheme
echo "[1/5] Installing EduOS color scheme..."
mkdir -p "$COLOR_DIR"
cp "$THEMES_SRC/EduOS-Colors/EduOS.colors" "$COLOR_DIR/"
echo "  → $COLOR_DIR/EduOS.colors"

# 2. Plasma theme
echo "[2/5] Installing Plasma desktop theme..."
mkdir -p "$PLASMA_THEME_DIR/EduOS-Plasma"
cp -r "$THEMES_SRC/EduOS-Plasma/"* "$PLASMA_THEME_DIR/EduOS-Plasma/"
echo "  → $PLASMA_THEME_DIR/EduOS-Plasma/"

# 3. SDDM theme (requires sudo)
echo "[3/5] Installing SDDM login theme..."
if command -v sudo &> /dev/null; then
    sudo mkdir -p "$SDDM_THEME_DIR/EduOS-SDDM"
    sudo cp -r "$THEMES_SRC/EduOS-SDDM/"* "$SDDM_THEME_DIR/EduOS-SDDM/"
    echo "  → $SDDM_THEME_DIR/EduOS-SDDM/"
else
    echo "  ⚠ Skipped (sudo not available)"
fi

# 4. Splash screen
echo "[4/5] Installing splash screen..."
mkdir -p "$SPLASH_DIR/EduOS-Splash"
cp -r "$THEMES_SRC/EduOS-Splash/"* "$SPLASH_DIR/EduOS-Splash/"
echo "  → $SPLASH_DIR/EduOS-Splash/"

# 5. Apply settings
echo "[5/5] Applying settings..."
kwriteconfig5 --file ~/.config/kdeglobals --group General --key ColorScheme "EduOS"
kwriteconfig5 --file ~/.config/plasmarc --group Theme --key name "EduOS-Plasma"
kwriteconfig5 --file ~/.config/ksplashrc --group KSplash --key Theme "EduOS-Splash"

# Set SDDM theme (requires root)
if command -v sudo &> /dev/null; then
    sudo kwriteconfig5 --file /etc/sddm.conf --group Theme --key Current "EduOS-SDDM" 2>/dev/null || true
fi

echo ""
echo "✅ EduOS Liquid Glass theme installed!"
echo ""
echo "To apply immediately:"
echo "  plasma-apply-colorscheme EduOS"
echo "  plasma-apply-desktoptheme EduOS-Plasma"
echo "  plasma-apply-splashscreen EduOS-Splash"
echo ""
echo "Restart Plasma:"
echo "  kquitapp5 plasmashell && kstart5 plasmashell &"
