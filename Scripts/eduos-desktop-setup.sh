#!/bin/bash
# EduOS Desktop Setup Script
# Configures KDE Plasma for an EduOS educational user
# Run as the target user after login
# Usage: eduos-desktop-setup.sh

set -e

echo "EduOS Desktop Setup"
echo "===================="

# 1. Apply EduOS color scheme
echo "  → Applying EduOS color scheme..."
plasma-apply-colorscheme EduOS 2>/dev/null || echo "  ⚠ Could not apply color scheme"

# 2. Set wallpaper
echo "  → Setting EduOS wallpaper..."
WALLPAPER="/opt/eduos/Branding/wallpaper/eduos-wallpaper.png"
if [ -f "$WALLPAPER" ]; then
  plasma-apply-wallpaperimage "$WALLPAPER" 2>/dev/null || \
  kwriteconfig6 --file ~/.config/plasma-org.kde.plasma.desktop-appletsrc \
    --group 'Containments][2][Wallpaper][org.kde.image][General' \
    --key Image "file://$WALLPAPER" 2>/dev/null || true
fi

# 3. Configure panel: reduce icon size, add EduOS launcher
echo "  → Optimizing panel..."
kwriteconfig6 --file ~/.config/plasma-org.kde.plasma.desktop-appletsrc \
  --group 'Containments][2][Applets][5][Configuration][General' \
  --key iconSize 3 2>/dev/null || true

# 4. Set application font
echo "  → Setting system fonts..."
kwriteconfig6 --file ~/.config/kdeglobals --group "General" --key "font" "Inter,10,-1,5,50,0,0,0,0,0" 2>/dev/null || true
kwriteconfig6 --file ~/.config/kdeglobals --group "General" --key "fixed" "Fira Code,10,-1,5,50,0,0,0,0,0" 2>/dev/null || true
kwriteconfig6 --file ~/.config/kdeglobals --group "General" --key "smallestReadableFont" "Inter,8,-1,5,50,0,0,0,0,0" 2>/dev/null || true

# 5. Disable Baloo file indexer
echo "  → Disabling file indexer..."
kwriteconfig6 --file ~/.config/baloofilerc --group "Basic Settings" --key "Indexing-Enabled" false 2>/dev/null || true

# 6. Disable screen lock for lab use
echo "  → Configuring security..."
kwriteconfig6 --file ~/.config/kscreenlockerrc --group "Daemon" --key "Autolock" false 2>/dev/null || true
kwriteconfig6 --file ~/.config/kscreenlockerrc --group "Daemon" --key "Timeout" 60 2>/dev/null || true

# 7. Reduce compositor animation
echo "  → Optimizing KWin compositor..."
kwriteconfig6 --file ~/.config/kwinrc --group "Compositing" --key "AnimationSpeed" 2 2>/dev/null || true
kwriteconfig6 --file ~/.config/kwinrc --group "Compositing" --key "HiddenPreviews" 0 2>/dev/null || true

echo ""
echo "✅ EduOS Desktop configured. Restart Plasma (Ctrl+Alt+Del) to see changes."
