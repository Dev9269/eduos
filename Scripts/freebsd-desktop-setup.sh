#!/bin/sh
# EduOS FreeBSD Desktop Setup
# Run as root on a fresh FreeBSD 14.x installation
# Usage: sh Scripts/freebsd-desktop-setup.sh

set -e

echo "╔══════════════════════════════════════════╗"
echo "║   EduOS FreeBSD Desktop Setup v2.0      ║"
echo "╚══════════════════════════════════════════╝"

# 1. Update pkg and install KDE Plasma
echo "[1/6] Installing KDE Plasma desktop..."
env ASSUME_ALWAYS_YES=YES pkg update
pkg install -y \
    xorg \
    kde5 \
    sddm \
    konsole \
    dolphin \
    plasma5-plasma-desktop \
    plasma5-plasma-workspace

# 2. Enable display manager
echo "[2/6] Enabling SDDM..."
sysrc sddm_enable="YES"
sysrc dbus_enable="YES"
sysrc hald_enable="YES"

# 3. Install Python and EduOS dependencies
echo "[3/6] Installing Python stack..."
pkg install -y python311 py311-pip
pip3.11 install \
    PyQt6 \
    cryptography \
    fastapi \
    uvicorn \
    websockets \
    psutil \
    pyjwt \
    bcrypt

# 4. Install development tools (Dev Suite)
echo "[4/6] Installing development tools..."
pkg install -y \
    git \
    gcc \
    python311 \
    openjdk17 \
    nodejs \
    npm \
    rust \
    go \
    nano \
    vim \
    tmux

# 5. Apply EduOS branding
echo "[5/6] Applying EduOS branding..."
mkdir -p /usr/local/share/wallpapers/EduOS
cp -r /opt/eduos/Branding/wallpaper/* \
    /usr/local/share/wallpapers/EduOS/ 2>/dev/null || true
mkdir -p /usr/local/share/sddm/themes/eduos
cp -r /opt/eduos/Branding/sddm/* \
    /usr/local/share/sddm/themes/eduos/ 2>/dev/null || true

# Configure SDDM to use EduOS theme
mkdir -p /usr/local/etc/sddm.conf.d
cat > /usr/local/etc/sddm.conf.d/eduos.conf << 'EOF'
[Theme]
Current=eduos

[Autologin]
User=student
Session=plasma.desktop
EOF

# 6. Install and start EduOS agent
echo "[6/6] Installing EduOS agent..."
cp /opt/eduos/Services/freebsd/eduos_agent \
    /usr/local/etc/rc.d/eduos_agent
chmod +x /usr/local/etc/rc.d/eduos_agent
sysrc eduos_agent_enable="YES"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   EduOS Desktop Setup COMPLETE           ║"
echo "║   Reboot to start desktop environment    ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "After reboot, the EduOS login screen will appear."
echo "Default user: student"
