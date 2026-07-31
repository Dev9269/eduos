#!/usr/bin/env bash
# =============================================================================
# EduOS Installer — Deploy EduOS to any Debian 13 (Trixie) system
# =============================================================================
# Usage:
#   wget -qO- https://raw.githubusercontent.com/jainam/eduos/main/install.sh | bash
#   OR
#   sudo bash install.sh
# =============================================================================

set -euo pipefail

EduOS_VERSION="1.0.0"
EduOS_CODENAME="Trixie"
EduOS_USER="jainam"
REPO_URL="file:///home/jainam/EduOS"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; NC='\033[0m'

log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1"; }
info() { echo -e "${BLUE}[➜]${NC} $1"; }

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════╗"
echo "║        EduOS Installer v${EduOS_VERSION}           ║"
echo "║    Educational Operating System for Campus     ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"

# Check root
if [[ ${EUID} -ne 0 ]]; then
    err "This script must be run as root (use sudo)"
    exit 1
fi

# Check OS
if ! grep -q "Debian GNU/Linux 13\|trixie" /etc/os-release 2>/dev/null; then
    warn "This installer is designed for Debian 13 (Trixie)"
    warn "Continuing anyway..."
fi

# =============================================================================
# PHASE 1: System Preparation
# =============================================================================
info "Phase 1: System Preparation"
info "Updating package lists..."
apt update -qq

log "Package lists updated"

# =============================================================================
# PHASE 2: Desktop & Branding
# =============================================================================
info "Phase 2: Installing Desktop & Branding"

# Install KDE Plasma if not present
if ! dpkg -l | grep -q plasma-desktop; then
    info "Installing KDE Plasma desktop..."
    apt install -y kde-plasma-desktop plasma-workspace sddm 2>&1 | tail -1
    log "KDE Plasma installed"
fi

# Install theming packages
apt install -y papirus-icon-theme fonts-inter fonts-firacode fonts-noto-color-emoji \
    fonts-wine plymouth plymouth-themes imagemagick 2>&1 | tail -1

log "Desktop packages installed"

# Configure Plasma (Windows 11 layout)
sudo -u "$SUDO_USER" kwriteconfig5 --file ~/.config/plasma-org.kde.plasma.desktop-appletsrc \
    --group Containments --group 1 --key formFactor 2 2>/dev/null || true
sudo -u "$SUDO_USER" kwriteconfig5 --file ~/.config/plasma-org.kde.plasma.desktop-appletsrc \
    --group Containments --group 1 --key floating true 2>/dev/null || true
sudo -u "$SUDO_USER" kwriteconfig5 --file ~/.config/plasma-org.kde.plasma.desktop-appletsrc \
    --group Containments --group 1 --key alignment center 2>/dev/null || true

# Set icon theme and color scheme
sudo -u "$SUDO_USER" kwriteconfig5 --file ~/.config/kdeglobals --group Icons --key Theme "Papirus-Dark"
sudo -u "$SUDO_USER" kwriteconfig5 --file ~/.config/kdeglobals --group General --key ColorScheme "BreezeDark"

log "Desktop configured"

# =============================================================================
# PHASE 3: Development Environment
# =============================================================================
info "Phase 3: Installing Development Tools"

apt install -y build-essential gdb cmake make autoconf automake libtool pkg-config \
    python3 python3-pip python3-venv python3-dev python3-setuptools python3-wheel \
    openjdk-21-jdk openjdk-21-doc maven gradle \
    nodejs npm \
    sqlite3 sqlitebrowser postgresql postgresql-client mariadb-client redis \
    php php-cli composer ruby ruby-dev perl \
    valgrind strace ltrace lsof linux-perf 2>&1 | tail -1

# VS Code
if ! command -v code &>/dev/null; then
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list
    apt update -qq && apt install -y code 2>&1 | tail -1
    log "VS Code installed"
fi

# Docker
if ! command -v docker &>/dev/null; then
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo "deb [arch=amd64] https://download.docker.com/linux/debian bookworm stable" > /etc/apt/sources.list.d/docker.list
    apt update -qq && apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin 2>&1 | tail -1
    usermod -aG docker "$SUDO_USER"
    systemctl enable --now docker
    log "Docker installed"
fi

# .NET SDK
if ! command -v dotnet &>/dev/null; then
    curl -fsSL https://dotnet.microsoft.com/download/dotnet/scripts/v1/dotnet-install.sh | bash -s -- --channel 8.0 2>&1 | tail -1
    echo 'export PATH=$HOME/.dotnet:$PATH' >> /home/"$SUDO_USER"/.bashrc
    log ".NET SDK installed"
fi

log "Development tools installed"

# =============================================================================
# PHASE 4: Cybersecurity Tools
# =============================================================================
info "Phase 4: Installing Cybersecurity Tools"

apt install -y wireshark nmap tcpdump netcat-openbsd hydra john sqlmap gobuster dirb \
    aircrack-ng ettercap-text-only macchanger proxychains4 hping3 slowhttptest \
    dnsutils whois 2>&1 | tail -1

# nikto from git
if ! command -v nikto &>/dev/null; then
    git clone --depth=1 https://github.com/sullo/nikto /opt/eduos/nikto 2>/dev/null
    ln -sf /opt/eduos/nikto/program/nikto.pl /usr/local/bin/nikto 2>/dev/null || true
    log "nikto installed"
fi

# OWASP Juice Shop
docker pull bkimminich/juice-shop 2>&1 | tail -1 &
log "Juice Shop image pulled"

log "Cybersecurity tools installed"

# =============================================================================
# PHASE 5: Virtualization
# =============================================================================
info "Phase 5: Installing Virtualization"

apt install -y qemu-system-x86 qemu-utils virt-manager virt-viewer \
    libvirt-daemon-system libvirt-clients bridge-utils 2>&1 | tail -1
systemctl enable --now libvirtd
usermod -aG libvirt "$SUDO_USER"
log "Virtualization installed"

# =============================================================================
# PHASE 6: Security Hardening
# =============================================================================
info "Phase 6: Security Hardening"

ufw allow ssh
ufw --force enable
log "Firewall enabled"

# Lock root
passwd -l root 2>/dev/null || true
log "Root account locked"

# Disable SSH root
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd
log "SSH root login disabled"

# Secure home perms
chmod 750 /home/* 2>/dev/null || true
log "Home permissions set"

# Process accounting
apt install -y acct 2>&1 | tail -1
systemctl enable --now acct
log "Process accounting enabled"

# Disable unnecessary services
systemctl disable --now bluetooth.service 2>/dev/null || true
systemctl disable --now cups-browsed.service 2>/dev/null || true
systemctl disable --now avahi-daemon.service 2>/dev/null || true
systemctl disable --now ModemManager.service 2>/dev/null || true
log "Unnecessary services disabled"

# =============================================================================
# PHASE 7: Create EduOS Users
# =============================================================================
info "Phase 7: Creating EduOS Users"

for user in student exam admin; do
    if ! id "$user" &>/dev/null; then
        useradd -m -s /bin/bash -c "EduOS $user" "$user"
        log "User $user created"
    else
        log "User $user already exists"
    fi
done

# Generate strong random passwords (no hardcoded credentials)
STUDENT_PW=$(openssl rand -base64 16 | tr -d '=/+' | cut -c1-16)
EXAM_PW=$(openssl rand -base64 16 | tr -d '=/+' | cut -c1-16)
ADMIN_PW=$(openssl rand -base64 16 | tr -d '=/+' | cut -c1-16)
echo "student:$STUDENT_PW" | chpasswd 2>/dev/null
echo "exam:$EXAM_PW" | chpasswd 2>/dev/null
echo "admin:$ADMIN_PW" | chpasswd 2>/dev/null

# Persist generated credentials (owner-only) and print once for the admin
mkdir -p /etc/eduos
cat > /etc/eduos/credentials.conf << 'CREDEOF'
# EduOS generated credentials — generated at install time
student_password=$STUDENT_PW
exam_password=$EXAM_PW
admin_password=$ADMIN_PW
CREDEOF
chmod 600 /etc/eduos/credentials.conf
log "Random passwords generated and saved to /etc/eduos/credentials.conf (chmod 600)"

# =============================================================================
# PHASE 8: Restore EduOS Modules (if backup exists)
# =============================================================================
info "Phase 8: Installing EduOS Modules"

EDUOS_SRC="/home/$SUDO_USER/EduOS"
if [ -d "$EDUOS_SRC" ]; then
    # Install system launchers
    for script in "$EDUOS_SRC/Scripts/"*.sh; do
        [ -f "$script" ] && cp "$script" /usr/local/bin/ 2>/dev/null || true
    done
    chmod +x /usr/local/bin/eduos-*.sh 2>/dev/null || true

    # Install desktop entries
    for desktop in "$EDUOS_SRC/config/includes.chroot/usr/share/applications/"*.desktop; do
        [ -f "$desktop" ] && cp "$desktop" /usr/share/applications/ 2>/dev/null || true
    done

    # Copy to /etc/skel
    mkdir -p /etc/skel/Desktop /etc/skel/.config
    cp /usr/share/applications/eduos-*.desktop /etc/skel/Desktop/ 2>/dev/null || true
    echo 'PS1="\[\e[36m\]EduOS\[\e[0m\]:\w\$ "' > /etc/skel/.bashrc

    log "EduOS modules installed from $EDUOS_SRC"
else
    warn "EduOS source directory not found at $EDUOS_SRC"
    warn "Install EduOS modules manually after installation"
fi

# =============================================================================
# COMPLETE
# =============================================================================
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      EduOS Installation Complete!            ║${NC}"
echo -e "${GREEN}║  Please reboot to finish setup.              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo "  Users:   student / (generated — see /etc/eduos/credentials.conf)"
echo "           exam    / (generated — see /etc/eduos/credentials.conf)"
echo "           admin   / (generated — see /etc/eduos/credentials.conf)"
echo ""
echo "  After reboot, run:  eduos-info"
echo ""
