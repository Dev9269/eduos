#!/bin/bash
# EduOS Desktop Layout Deployer
# Applies the Windows-style taskbar layout to all EduOS users.
# Also copies EduOS app shortcuts to the Desktop for easy discovery.
#
# Usage: sudo ./eduos-apply-desktop-layout.sh [username]

set -e

EDUOS_DIR="/opt/eduos"
LAYOUT_SCRIPT="$EDUOS_DIR/Scripts/eduos-desktop-layout.py"
WALLPAPER_SRC="$EDUOS_DIR/Branding/wallpaper/eduos-wallpaper.png"
WALLPAPER_DST="/usr/share/wallpapers/eduos-wallpaper.png"
COLOR_SCHEME="/usr/share/color-schemes/EduOS.colors"

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log()  { echo -e "${BLUE}[EduOS]${NC} $1"; }
ok()   { echo -e "${GREEN}  ✅ $1${NC}"; }
warn() { echo -e "${YELLOW}  ⚠️  $1${NC}"; }

# Ensure wallpaper is accessible system-wide
setup_wallpaper() {
    if [ -f "$WALLPAPER_SRC" ] && [ ! -f "$WALLPAPER_DST" ]; then
        cp "$WALLPAPER_SRC" "$WALLPAPER_DST"
        ok "Wallpaper copied to $WALLPAPER_DST"
    elif [ -f "$WALLPAPER_DST" ]; then
        ok "Wallpaper already accessible system-wide"
    fi
}

# Apply layout for a single user
apply_for_user() {
    local username="$1"
    local user_home

    user_home=$(getent passwd "$username" | cut -d: -f6)
    if [ -z "$user_home" ] || [ ! -d "$user_home" ]; then
        warn "Home directory for '$username' not found, skipping"
        return 1
    fi

    log "Applying layout for user: $username"

    # Create .config if it doesn't exist
    mkdir -p "$user_home/.config"

    # Backup existing config
    if [ -f "$user_home/.config/plasma-org.kde.plasma.desktop-appletsrc" ]; then
        cp "$user_home/.config/plasma-org.kde.plasma.desktop-appletsrc" \
           "$user_home/.config/plasma-org.kde.plasma.desktop-appletsrc.eduos-backup"
    fi

    # Copy the reference Mac layout from jainam, then adjust wallpaper path
    REFERENCE="/etc/skel/.config/plasma-org.kde.plasma.desktop-appletsrc"
    TEMP_FILE="/tmp/eduos-layout-$username.tmp"
    if [ -f "$REFERENCE" ]; then
        # Use a temp file to avoid reading/writing same file (bash truncation issue)
        sed "s|Image=file:///opt/eduos/Branding/wallpaper/eduos-wallpaper.png|Image=file://${WALLPAPER_DST}|g; s|Image=file:///usr/share/wallpapers/eduos-wallpaper.png|Image=file://${WALLPAPER_DST}|g" \
            "$REFERENCE" > "$TEMP_FILE"
        cp "$TEMP_FILE" "$user_home/.config/plasma-org.kde.plasma.desktop-appletsrc"
        rm -f "$TEMP_FILE"
    fi

    # Set KWin settings for this user
    mkdir -p "$user_home/.config"
    kwriteconfig6 --file "$user_home/.config/kwinrc" \
        --group Compositing --key AnimationSpeed "1"
    kwriteconfig6 --file "$user_home/.config/kwinrc" \
        --group Compositing --key Enabled "true"
    kwriteconfig6 --file "$user_home/.config/kwinrc" \
        --group Compositing --key MaxFps "60"
    kwriteconfig6 --file "$user_home/.config/kwinrc" \
        --group Compositing --key WindowsBlockCompositing "false"
    kwriteconfig6 --file "$user_home/.config/kwinrc" \
        --group org.kde.kdecoration2 --key theme "Breeze"

    # Set global theme preferences
    kwriteconfig6 --file "$user_home/.config/kdeglobals" \
        --group General --key ColorScheme "EduOS"
    kwriteconfig6 --file "$user_home/.config/kdeglobals" \
        --group Icons --key Theme "Papirus-Dark"

    # Copy EduOS color scheme to user's local config as fallback
    if [ -f "$COLOR_SCHEME" ]; then
        mkdir -p "$user_home/.local/share/color-schemes/"
        cp "$COLOR_SCHEME" "$user_home/.local/share/color-schemes/"
    fi

    # Copy EduOS desktop icons for easy app discovery
    mkdir -p "$user_home/Desktop"
    EDUOS_APPS="eduos-demo-exam eduos-learnhub eduos-devsuite eduos-cyberlab eduos-admincenter eduos-exammode eduos-welcome"
    for app in $EDUOS_APPS; do
        if [ -f "/usr/share/applications/${app}.desktop" ]; then
            cp "/usr/share/applications/${app}.desktop" "$user_home/Desktop/"
        fi
    done
    for app in firefox-esr org.kde.dolphin org.kde.konsole systemsettings; do
        if [ -f "/usr/share/applications/${app}.desktop" ]; then
            cp "/usr/share/applications/${app}.desktop" "$user_home/Desktop/"
        fi
    done
    chmod +x "$user_home/Desktop/"*.desktop 2>/dev/null
    chown -R "$username:$username" "$user_home/Desktop" 2>/dev/null || true

    # Fix ownership
    chown -R "$username:$username" "$user_home/.config/plasma-org.kde.plasma.desktop-appletsrc" \
        "$user_home/.config/kwinrc" \
        "$user_home/.config/kdeglobals" 2>/dev/null || true

    # Restore keyboard shortcuts for search and terminal
    kwriteconfig6 --file "$user_home/.config/kglobalshortcutsrc" \
        --group krunner --key "_launch" "Alt+Space\tAlt+F2\tSearch" 2>/dev/null || true
    kwriteconfig6 --file "$user_home/.config/kglobalshortcutsrc" \
        --group org.kde.konsole --key "_launch" "Ctrl+Alt+T\t\tKonsole" 2>/dev/null || true

    ok "Layout applied for $username"
}

# Setup /etc/skel for new users
setup_skel() {
    log "Setting up /etc/skel for new users..."

    # Create skel .config directory
    mkdir -p /etc/skel/.config

    # Copy the reference Mac layout from jainam (avoid $HOME - it's /root when sudo)
    REFERENCE="/etc/skel/.config/plasma-org.kde.plasma.desktop-appletsrc"
    if [ -f "$REFERENCE" ]; then
        sed "s|Image=file:///opt/eduos/Branding/wallpaper/eduos-wallpaper.png|Image=file://${WALLPAPER_DST}|g; s|Image=file:///usr/share/wallpapers/eduos-wallpaper.png|Image=file://${WALLPAPER_DST}|g" \
            "$REFERENCE" > /etc/skel/.config/plasma-org.kde.plasma.desktop-appletsrc
    fi

    # Copy KWin settings from jainam
    if [ -f "/etc/skel/.config/kwinrc" ]; then
        cp "/etc/skel/.config/kwinrc" /etc/skel/.config/kwinrc
    fi

    # Copy kdeglobals from jainam
    if [ -f "/etc/skel/.config/kdeglobals" ]; then
        cp "/etc/skel/.config/kdeglobals" /etc/skel/.config/kdeglobals
    fi

    # Create local color-schemes directory
    mkdir -p /etc/skel/.local/share/color-schemes/
    if [ -f "$COLOR_SCHEME" ]; then
        cp "$COLOR_SCHEME" /etc/skel/.local/share/color-schemes/
    fi

    # Copy keyboard shortcuts for search and terminal
    kwriteconfig6 --file /etc/skel/.config/kglobalshortcutsrc \
        --group krunner --key "_launch" "Alt+Space\tAlt+F2\tSearch" 2>/dev/null || true
    kwriteconfig6 --file /etc/skel/.config/kglobalshortcutsrc \
        --group org.kde.konsole --key "_launch" "Ctrl+Alt+T\t\tKonsole" 2>/dev/null || true

    # Copy desktop icons for easy app discovery
    mkdir -p /etc/skel/Desktop
    for app in eduos-demo-exam eduos-learnhub eduos-devsuite eduos-cyberlab eduos-admincenter eduos-exammode eduos-welcome firefox-esr org.kde.dolphin org.kde.konsole systemsettings; do
        if [ -f "/usr/share/applications/${app}.desktop" ]; then
            cp "/usr/share/applications/${app}.desktop" /etc/skel/Desktop/
        fi
    done
    chmod +x /etc/skel/Desktop/*.desktop 2>/dev/null

    ok "/etc/skel configured for new users"
}

# Main
echo "╔══════════════════════════════════════════════╗"
echo "║   EduOS Desktop Layout - Multi-User Deploy   ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This script must be run as root (sudo)."
    exit 1
fi

setup_wallpaper

if [ -n "$1" ]; then
    # Apply for specific user
    if id "$1" &>/dev/null; then
        apply_for_user "$1"
    else
        echo "❌ User '$1' does not exist."
        exit 1
    fi
else
    # Apply for all EduOS users
    log "Applying layout for all EduOS users..."
    for user in jainam student exam admin; do
        if id "$user" &>/dev/null; then
            apply_for_user "$user"
        fi
    done
fi

# Setup skel
setup_skel

echo ""
echo "✨ Desktop layout deployment complete!"
echo ""
echo "Users must log out and log back in to see the new layout."
echo "Or run: systemctl --user restart plasma-plasmashell.service"
