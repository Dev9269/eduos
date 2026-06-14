#!/usr/bin/env bash
set -euo pipefail
BACKUP_DIR=~/EduOS/Backups/$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"

# Backup critical system configurations
sudo cp -r /etc/default "$BACKUP_DIR/etc-default" 2>/dev/null || true
sudo cp -r /etc/apt "$BACKUP_DIR/etc-apt" 2>/dev/null || true
sudo cp -r /etc/sddm.conf.d 2>/dev/null "$BACKUP_DIR/sddm" 2>/dev/null || true
sudo cp -r /etc/plymouth "$BACKUP_DIR/plymouth" 2>/dev/null || true
sudo cp -r /etc/systemd "$BACKUP_DIR/systemd" 2>/dev/null || true
cp -r ~/.config "$BACKUP_DIR/user-config" 2>/dev/null || true
cp -r ~/.local/share/plasma "$BACKUP_DIR/plasma" 2>/dev/null || true

# Package list
dpkg-query -l > "$BACKUP_DIR/packages.txt"
echo "Backup saved to: $BACKUP_DIR"
