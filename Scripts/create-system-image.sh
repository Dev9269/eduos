#!/usr/bin/env bash
# =============================================================================
# EduOS System Image Creator — Create bootable backup/install image
# =============================================================================
# Creates a compressed system image that can be restored on another machine
# or used as a deployment baseline.
# =============================================================================

set -euo pipefail

IMAGE_DIR="/home/jainam/EduOS/Packages"
IMAGE_NAME="eduos-$(date +%Y%m%d)-system-image.tar.gz"
EXCLUDES="--exclude=/proc --exclude=/sys --exclude=/dev --exclude=/run --exclude=/mnt --exclude=/media --exclude=/lost+found --exclude=/tmp --exclude=/var/cache/apt --exclude=/var/log --exclude=/home/*/.cache --exclude=/home/*/.local/share/Trash --exclude=/home/*/Downloads/* --exclude=/home/*/Desktop/* --exclude=/home/*/Documents/*"

echo "╔══════════════════════════════════════════════╗"
echo "║      EduOS System Image Creator              ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "This will create a compressed system image of this EduOS installation."
echo "The image can be restored on another machine with identical hardware."
echo ""
echo "Output: $IMAGE_DIR/$IMAGE_NAME"
echo ""

mkdir -p "$IMAGE_DIR"

if [ -f "$IMAGE_DIR/$IMAGE_NAME" ]; then
    echo "Previous image exists. Overwriting..."
    rm -f "$IMAGE_DIR/$IMAGE_NAME"
fi

echo "📦 Creating system image (this may take a while)..."
tar czpf "$IMAGE_DIR/$IMAGE_NAME" $EXCLUDES / 2>&1 | tail -1

echo ""
echo "✅ Image created!"
ls -lh "$IMAGE_DIR/$IMAGE_NAME"
echo ""
echo "Size: $(du -h "$IMAGE_DIR/$IMAGE_NAME" | cut -f1)"
echo ""
echo "To restore this image on another machine:"
echo "  1. Boot a Live Debian USB"
echo "  2. Partition the target disk"
echo "  3. Run: sudo tar xzpf $IMAGE_NAME -C /mnt"
echo "  4. Run: sudo grub-install --boot-directory=/mnt/boot /dev/sda"
echo ""
