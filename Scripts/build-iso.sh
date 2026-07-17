#!/bin/bash
# EduOS v3 ISO Builder - builds all packages and generates bootable ISO
set -e
PROJECT_DIR="/root/edos-build"
PACKAGES_DIR="$PROJECT_DIR/packages"
BUILD_DIR="$PROJECT_DIR/build"
ISO_DIR="$PROJECT_DIR/iso"
LOG_FILE="$PROJECT_DIR/build.log"

echo "=== EduOS v3 ISO Build ==="
date

echo "[1] Installing build dependencies..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq 2>/dev/null || true
apt-get install -y -qq debhelper dh-python python3 2>/dev/null || true

echo "[2] Building all packages..."
cd "$PACKAGES_DIR"
for pkg in eduos-*/; do
    pkg_name="${pkg%/}"
    if [ -f "$pkg_name/debian/control" ]; then
        echo "  Building $pkg_name..."
        cd "$PACKAGES_DIR/$pkg_name"
        dpkg-buildpackage -b -uc -us 2>&1 | tail -3 || echo "  WARNING: $pkg_name build had issues"
        cd "$PACKAGES_DIR"
    fi
done

echo "[3] Staging packages..."
mkdir -p "$BUILD_DIR/config/packages.chroot"
cp -v "$PACKAGES_DIR"/*.deb "$BUILD_DIR/config/packages.chroot/" 2>/dev/null || true

echo "[4] Reconfiguring live-build..."
cd "$BUILD_DIR"
lb clean 2>/dev/null || true
lb config \
    --distribution trixie \
    --architectures amd64 \
    --linux-flavours amd64 \
    --debian-installer false \
    --bootappend-live "boot=live components quiet splash username=edos" \
    --bootloaders grub-efi \
    --archive-areas "main contrib non-free non-free-firmware" \
    --updates true \
    --security true \
    --backports true \
    --iso-application "EduOS" \
    --iso-preparer "EduOS Team" \
    --iso-publisher "EduOS" \
    --iso-volume "EduOS v3.0" \
    --firmware-binary true \
    --firmware-chroot true \
    --memtest none

echo "[5] Building ISO (this will take a while)..."
lb build 2>&1 | tee "$LOG_FILE"

echo "[6] Collecting output..."
mkdir -p "$ISO_DIR"
cp -v live-image-amd64.hybrid.iso "$ISO_DIR/EduOS-v3.0.iso" 2>/dev/null || \
cp -v live-image-amd64.iso "$ISO_DIR/EduOS-v3.0.iso" 2>/dev/null || true

if [ -f "$ISO_DIR/EduOS-v3.0.iso" ]; then
    echo "SUCCESS: ISO built at $ISO_DIR/EduOS-v3.0.iso"
    ls -lh "$ISO_DIR/EduOS-v3.0.iso"
else
    echo "ISO not found - checking build directory..."
    ls "$BUILD_DIR/"
fi
