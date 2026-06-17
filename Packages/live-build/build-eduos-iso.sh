#!/usr/bin/env bash
# =============================================================================
# EduOS ISO Builder v1.0 — Creates installable EduOS Hybrid Live/Install ISO
# =============================================================================
# Usage:
#   sudo ./build-eduos-iso.sh
#
# Requirements:
#   - Debian 13 (Trixie) or later
#   - live-build package installed
#   - ~10 GB free disk space for the build
# =============================================================================
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
    echo "Run as root: sudo ./build-eduos-iso.sh"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR/work"
OUTPUT_DIR="$SCRIPT_DIR/output"
EDUOS_REPO="${EDUOS_REPO:-/home/jainam/EduOS}"
DATE=$(date +%Y%m%d)

echo "╔══════════════════════════════════════════════╗"
echo "║        EduOS ISO Builder v1.0                 ║"
echo "╚══════════════════════════════════════════════╝"

# Check live-build is installed
if ! command -v lb &>/dev/null; then
    echo "Installing live-build..."
    apt-get install -y -qq live-build debootstrap
fi

mkdir -p "$WORK_DIR" "$OUTPUT_DIR"

# Clean previous build
if [ -d "$WORK_DIR" ]; then
    cd "$WORK_DIR"
    lb clean 2>/dev/null || true
fi

cd "$WORK_DIR"

# ── Configure the build ────────────────────────────────────────────
lb config \
    --distribution trixie \
    --archive-areas "main contrib non-free-firmware" \
    --binary-images iso-hybrid \
    --debian-installer live \
    --bootappend-live "boot=live components username=student hostname=eduos locales=en_US.UTF-8 keyboard-layouts=us" \
    --bootappend-install "username=student hostname=eduos" \
    --iso-application "EduOS Educational Operating System" \
    --iso-preparer "EduOS Team" \
    --iso-publisher "EduOS" \
    --iso-volume "EduOS $DATE" \
    --memtest none \
    --firmware-binary true \
    --firmware-chroot true \
    --apt-recommends false \
    --apt-indices false

echo "✅ Build configured"

# ── Package lists ──────────────────────────────────────────────────
mkdir -p config/package-lists

# Core desktop
cat > config/package-lists/eduos-core.list.chroot << 'EOF'
plasma-desktop
plasma-workspace
plasma-pa
plasma-nm
plasma-systemmonitor
plasma-browser-integration
kde-config-gtk-style
kde-config-gtk-style-preview
kde-config-screenlocker
kde-config-sddm
kde-spectacle
kwin-x11
sddm
sddm-theme-breeze
dolphin
konsole
kate
kwrite
gwenview
okular
kcalc
ark
khelpcenter
kinfocenter
firefox-esr
systemsettings
fonts-inter
fonts-firacode
fonts-noto
fonts-noto-color-emoji
fonts-liberation
papirus-icon-theme
breeze-icon-theme
breeze-gtk-theme
EOF

# Office & PDF
cat > config/package-lists/eduos-office.list.chroot << 'EOF'
libreoffice-writer
libreoffice-calc
libreoffice-impress
libreoffice-draw
libreoffice-math
libreoffice-kf6
libreoffice-qt6
libreoffice-style-breeze
poppler-utils
poppler-data
pdfarranger
ghostscript
mythes-en-us
EOF

# Development
cat > config/package-lists/eduos-dev.list.chroot << 'EOF'
build-essential
gcc
g++
gdb
cmake
make
git
python3
python3-pip
python3-venv
python3-dev
python3-pyqt6
python3-flask
python3-cryptography
python3-bcrypt
python3-reportlab
python3-pil
python3-bs4
python3-requests
python3-numpy
python3-scipy
python3-matplotlib
python3-pandas
python3-impacket
python3-libvirt
jupyter-notebook
default-jdk
default-jdk-headless
maven
gradle
nodejs
npm
ruby
ruby-dev
php
php-cli
php-xml
perl
sqlite3
sqlitebrowser
postgresql-client
valgrind
EOF

# Cybersecurity
cat > config/package-lists/eduos-cyber.list.chroot << 'EOF'
nmap
tcpdump
wireshark
netcat-openbsd
socat
hydra
john
sqlmap
gobuster
dirb
aircrack-ng
ettercap-text-only
macchanger
proxychains4
hping3
ufw
EOF

# Virtualization & Docker
cat > config/package-lists/eduos-virt.list.chroot << 'EOF'
qemu-system-x86
qemu-system-gui
qemu-utils
libvirt-daemon-system
libvirt-clients
virt-manager
virt-viewer
docker-ce
docker-ce-cli
docker-compose-plugin
containerd.io
EOF

echo "✅ Package lists created"

# ── Branding & config includes ─────────────────────────────────────
mkdir -p config/includes.chroot/usr/local/bin
mkdir -p config/includes.chroot/usr/share/applications
mkdir -p config/includes.chroot/usr/share/wallpapers
mkdir -p config/includes.chroot/usr/share/sddm/themes/eduos
mkdir -p config/includes.chroot/usr/share/plymouth/themes/eduos
mkdir -p config/includes.chroot/usr/share/color-schemes
mkdir -p config/includes.chroot/etc/skel/Desktop
mkdir -p config/includes.chroot/etc/skel/.config
mkdir -p config/includes.chroot/etc/
mkdir -p config/includes.chroot/opt/eduos

# Wallpaper
if [ -f "$EDUOS_REPO/Branding/wallpaper/eduos-wallpaper.png" ]; then
    cp "$EDUOS_REPO/Branding/wallpaper/eduos-wallpaper.png" \
       config/includes.chroot/usr/share/wallpapers/eduos-wallpaper.png
    echo "✅ Wallpaper copied"
fi

# SDDM theme
if [ -f "$EDUOS_REPO/Branding/sddm/Main.qml" ]; then
    cp "$EDUOS_REPO/Branding/sddm/"* config/includes.chroot/usr/share/sddm/themes/eduos/ 2>/dev/null || true
elif [ -d "$EDUOS_REPO/../usr/share/sddm/themes/eduos" ]; then
    cp -r /usr/share/sddm/themes/eduos/* config/includes.chroot/usr/share/sddm/themes/eduos/
    echo "✅ SDDM theme copied (from system install)"
fi

# Color scheme
if [ -f "$EDUOS_REPO/Branding/plasma/eduos.colors" ]; then
    cp "$EDUOS_REPO/Branding/plasma/eduos.colors" \
       config/includes.chroot/usr/share/color-schemes/EduOS.colors
    echo "✅ Color scheme copied"
fi

# Plymouth theme
if [ -d "$EDUOS_REPO/Branding/plymouth" ]; then
    cp -r "$EDUOS_REPO/Branding/plymouth/"* config/includes.chroot/usr/share/plymouth/themes/eduos/ 2>/dev/null || true
    echo "✅ Plymouth theme copied"
fi

# EduOS System Info
cat > config/includes.chroot/etc/eduos-release << 'EOF'
EduOS 1.0.0 (Trixie)
Educational Operating System
Built from Debian 13
EOF

# MOTD
cat > config/includes.chroot/etc/motd << 'EOF'
╔═══════════════════════════════════════════════╗
║              EduOS - Educational OS           ║
║     Debian-based | KDE Plasma | Secure Campus  ║
╚═══════════════════════════════════════════════╝
EOF

# Hostname
echo "eduos" > config/includes.chroot/etc/hostname
echo "127.0.1.1 eduos" >> config/includes.chroot/etc/hosts

# SDDM config
mkdir -p config/includes.chroot/etc/sddm.conf.d
cat > config/includes.chroot/etc/sddm.conf.d/eduos.conf << 'SDDMEOF'
[Theme]
Current=eduos
CursorTheme=breeze_cursors
Font=Inter,10

[General]
HaltCommand=/usr/bin/systemctl poweroff
RebootCommand=/usr/bin/systemctl reboot
InputMethod=
SDDMEOF

# Default user config
cat > config/includes.chroot/etc/skel/.config/kdeglobals << 'KEGEOF'
[General]
ColorScheme=EduOS

[Icons]
Theme=Papirus-Dark
KEGEOF

# Desktop shortcuts for all users
for app in firefox-esr org.kde.dolphin org.kde.konsole systemsettings; do
    if [ -f "/usr/share/applications/${app}.desktop" ]; then
        cp "/usr/share/applications/${app}.desktop" \
           config/includes.chroot/etc/skel/Desktop/
    fi
done
chmod +x config/includes.chroot/etc/skel/Desktop/*.desktop 2>/dev/null || true

echo "✅ Branding and configs installed"

# ── Install EduOS applications from repo ───────────────────────────
if [ -d "$EDUOS_REPO" ]; then
    # Copy Python source (will be installed by postinst or first-boot)
    mkdir -p config/includes.chroot/opt/eduos
    for dir in ExamMode AdminCenter LearnHub DevSuite CyberLab Scripts; do
        if [ -d "$EDUOS_REPO/$dir" ]; then
            cp -r "$EDUOS_REPO/$dir" config/includes.chroot/opt/eduos/
        fi
    done
    echo "✅ EduOS applications copied to /opt/eduos/"
fi

# Create launcher symlinks
mkdir -p config/includes.chroot/usr/local/bin
cat > config/includes.chroot/usr/local/bin/eduos-exam << 'EOF'
#!/bin/bash
python3 /opt/eduos/ExamMode/exam_app.py
EOF
chmod +x config/includes.chroot/usr/local/bin/eduos-exam

# ── Build hooks ────────────────────────────────────────────────────
mkdir -p config/hooks/live
cat > config/hooks/live/eduos-setup.hook.chroot << 'HOOKEOF'
#!/bin/bash
# EduOS first-boot setup hook

# Enable Plymouth
plymouth-set-default-theme eduos 2>/dev/null || true

# Enable UFW
ufw --force enable 2>/dev/null || true
ufw allow ssh 2>/dev/null || true

# Set default session to Plasma (X11)
update-alternatives --set x-session-manager /usr/bin/startplasma-x11 2>/dev/null || true

# Create EduOS users
useradd -m -s /bin/bash student 2>/dev/null || true
useradd -m -s /bin/bash admin 2>/dev/null || true
useradd -m -s /usr/local/bin/eduos-exam-shell exam 2>/dev/null || true

# Set passwords
echo "student:student123" | chpasswd 2>/dev/null || true
echo "admin:admin123" | chpasswd 2>/dev/null || true
echo "exam:exam123" | chpasswd 2>/dev/null || true

# Sudo for admin
usermod -aG sudo admin 2>/dev/null || true
echo "admin ALL=(ALL) ALL" >> /etc/sudoers.d/eduos-admin 2>/dev/null || true

# Clean up
apt-get clean
rm -rf /var/lib/apt/lists/*
HOOKEOF
chmod +x config/hooks/live/eduos-setup.hook.chroot

echo "✅ Build hooks created"

# ── Build the ISO ──────────────────────────────────────────────────
echo ""
echo "┌─────────────────────────────────────────────┐"
echo "│ Building EduOS ISO (this will take time...) │"
echo "└─────────────────────────────────────────────┘"
echo ""

lb build 2>&1 | tee "$OUTPUT_DIR/build.log"

# Copy result
if [ -f "live-image-amd64.hybrid.iso" ]; then
    mv live-image-amd64.hybrid.iso "$OUTPUT_DIR/eduos-$DATE-amd64.iso"
    echo ""
    echo "✅ ISO built successfully!"
    echo "   Location: $OUTPUT_DIR/eduos-$DATE-amd64.iso"
    echo "   Size: $(du -h "$OUTPUT_DIR/eduos-$DATE-amd64.iso" | cut -f1)"
else
    echo "❌ ISO build failed. Check $OUTPUT_DIR/build.log"
    exit 1
fi
