#!/usr/bin/env bash
# =============================================================================
# EduOS ISO Builder — Creates installable EduOS Live ISO
# =============================================================================
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
    echo "Run as root: sudo ./build-eduos-iso.sh"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR/work"
OUTPUT_DIR="$SCRIPT_DIR/output"
EDUOS_REPO="/home/jainam/EduOS"
DATE=$(date +%Y%m%d)

echo "╔══════════════════════════════════════════════╗"
echo "║        EduOS ISO Builder v1.0                 ║"
echo "╚══════════════════════════════════════════════╝"

mkdir -p "$WORK_DIR" "$OUTPUT_DIR"

# Clean previous build
if [ -d "$WORK_DIR" ]; then
    cd "$WORK_DIR"
    lb clean 2>/dev/null || true
fi

cd "$WORK_DIR"

# Configure the build
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
    --memtest memtest86+ \
    --firmware-binary true \
    --firmware-chroot true

echo "✅ Build configured"

# Install EduOS package lists
mkdir -p config/package-lists

# Desktop and core packages
cat > config/package-lists/eduos-desktop.list.chroot << 'PKGLIST'
task-gnome-desktop
plasma-desktop
plasma-workspace
sddm
firefox-esr
libreoffice
evince
file-roller
zenity
kate
konsole
gwenview
okular
gimp
kcalc
dolphin
systemsettings
ark
kwalletmanager
ksystemlog
p7zip-full
unrar-free
curl
wget
htop
ufw
rsync
git
vim
nano
fonts-inter
fonts-firacode
fonts-noto-color-emoji
fonts-wine
PKGLIST

# Development tools
cat > config/package-lists/eduos-dev.list.chroot << 'DEVEOF'
build-essential
gdb
cmake
make
autoconf
automake
libtool
pkg-config
python3
python3-pip
python3-venv
python3-dev
openjdk-21-jdk
openjdk-21-doc
maven
gradle
nodejs
npm
sqlite3
sqlitebrowser
postgresql
postgresql-client
mariadb-client
redis
php
php-cli
composer
ruby
ruby-dev
perl
valgrind
strace
ltrace
lsof
linux-perf
DEVEOf

# Cybersecurity tools
cat > config/package-lists/eduos-cyber.list.chroot << 'CYBEOF'
wireshark
nmap
tcpdump
netcat-openbsd
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
slowhttptest
dnsutils
whois
podman
podman-compose
qemu-system-x86
virt-manager
libvirt-daemon-system
bridge-utils
code
docker-ce
docker-ce-cli
containerd.io
docker-compose-plugin
CYBEOF

# EduOS branding and config
mkdir -p config/includes.chroot/usr/local/bin
mkdir -p config/includes.chroot/usr/share/applications
mkdir -p config/includes.chroot/usr/share/plymouth/themes
mkdir -p config/includes.chroot/etc/skel/Desktop
mkdir -p config/includes.chroot/etc/skel/.config

# Copy EduOS assets from repo
if [ -d "$EDUOS_REPO/Scripts" ]; then
    cp -r "$EDUOS_REPO/Scripts"/*.sh config/includes.chroot/usr/local/bin/ 2>/dev/null || true
fi

if [ -d "$EDUOS_REPO/Branding/wallpaper" ]; then
    cp "$EDUOS_REPO/Branding/wallpaper/eduos-wallpaper.png" config/includes.chroot/usr/share/wallpapers/ 2>/dev/null || true
fi

# Create MOTD
cat > config/includes.chroot/etc/motd << 'MOTD'
╔═══════════════════════════════════════════════╗
║              EduOS - Educational OS           ║
║     Debian-based | KDE Plasma | Secure Campus  ║
╚═══════════════════════════════════════════════╝
MOTD

# Create hostname
echo "eduos" > config/includes.chroot/etc/hostname
echo "127.0.1.1 eduos" > config/includes.chroot/etc/hosts

echo "✅ Package lists and configs installed"

# Build the ISO
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
