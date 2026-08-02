#!/usr/bin/env sh
# =============================================================================
# EduOS Installer v2.0 — Deploy EduOS on FreeBSD or Debian/Ubuntu
# =============================================================================
set -e

EDUOS_VERSION="2.0.0"
REPO_URL="https://github.com/Dev9269/eduos.git"
INSTALL_DIR="/opt/eduos"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; NC='\033[0m'

log()  { printf "${GREEN}[✓]${NC} %s\n" "$1"; }
warn() { printf "${YELLOW}[!]${NC} %s\n" "$1"; }
err()  { printf "${RED}[✗]${NC} %s\n" "$1"; exit 1; }
info() { printf "${BLUE}[➜]${NC} %s\n" "$1"; }

printf "${BLUE}"
echo "╔══════════════════════════════════════════════╗"
echo "║        EduOS Installer v${EDUOS_VERSION}         ║"
echo "║    Educational OS for Engineering Colleges   ║"
echo "╚══════════════════════════════════════════════╝"
printf "${NC}\n"

# Detect OS
OS=$(uname -s)
info "Detected OS: $OS"

case "$OS" in
  FreeBSD)
    PKG_INSTALL="pkg install -y"
    PYTHON="python3.11"
    PIP="pip3.11"
    SERVICE_DIR="/usr/local/etc/rc.d"
    log "FreeBSD detected — using pkg"
    ;;
  Linux)
    if command -v apt-get >/dev/null 2>&1; then
      PKG_INSTALL="apt-get install -y"
      PYTHON="python3"
      PIP="pip3"
      SERVICE_DIR="/etc/systemd/system"
      log "Debian/Ubuntu detected — using apt"
    else
      err "Unsupported Linux distribution. Use FreeBSD or Debian/Ubuntu."
    fi
    ;;
  *)
    err "Unsupported OS: $OS. EduOS runs on FreeBSD 14+ or Debian/Ubuntu."
    ;;
esac

# Check root
if [ "$(id -u)" -ne 0 ]; then
  err "Run as root: sudo sh Scripts/install-eduos.sh"
fi

# Install dependencies
info "Installing system dependencies..."
case "$OS" in
  FreeBSD)
    $PKG_INSTALL python311 py311-pip git curl wget || warn "Some packages failed"
    ;;
  Linux)
    apt-get update -qq
    $PKG_INSTALL python3 python3-pip git curl wget || warn "Some packages failed"
    ;;
esac

# Install Python packages
info "Installing Python dependencies..."
$PIP install --quiet \
  fastapi uvicorn websockets psutil pyjwt bcrypt cryptography slowapi \
  PyQt6 flask 2>/dev/null || warn "Some pip packages failed"

# Clone or update repo
if [ -d "$INSTALL_DIR/.git" ]; then
  info "Updating existing EduOS installation..."
  cd "$INSTALL_DIR" && git pull
else
  info "Cloning EduOS to $INSTALL_DIR..."
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

# Install agent service
info "Installing EduOS agent..."
case "$OS" in
  FreeBSD)
    cp "$INSTALL_DIR/Services/freebsd/eduos_agent" "$SERVICE_DIR/eduos_agent"
    chmod +x "$SERVICE_DIR/eduos_agent"
    sysrc eduos_agent_enable="YES" 2>/dev/null || true
    ;;
  Linux)
    cp "$INSTALL_DIR/Services/eduos-agent.service" "$SERVICE_DIR/"
    systemctl daemon-reload
    systemctl enable eduos-agent 2>/dev/null || true
    ;;
esac

# Create agent config if missing
mkdir -p /etc/eduos
if [ ! -f /etc/eduos/agent.conf ]; then
  printf '{"server_url": "ws://eduos-server.local:8765", "token": ""}\n' \
    > /etc/eduos/agent.conf
  chmod 600 /etc/eduos/agent.conf
  warn "Edit /etc/eduos/agent.conf to set your server IP and auth token"
fi

log "EduOS installed successfully at $INSTALL_DIR"
printf "\nNext steps:\n"
printf "  1. On admin laptop: bash $INSTALL_DIR/Server/start-server.sh\n"
printf "  2. Generate token: python3 $INSTALL_DIR/Server/generate-admin-token.py\n"
printf "  3. Edit /etc/eduos/agent.conf with server IP and token\n"
printf "  4. Start agent: service eduos_agent start (FreeBSD) or systemctl start eduos-agent (Linux)\n\n"
