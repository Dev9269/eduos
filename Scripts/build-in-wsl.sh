#!/bin/bash
# Run this from WSL (or it auto-detects)
PROJECT_DIR="/mnt/c/Users/jaina/EduOS"
WSL_DIR="/root/edos-build"

# Copy project to WSL
rsync -av --exclude='.git' --exclude='__pycache__' "$PROJECT_DIR/" "$WSL_DIR/"

# Install build dependencies
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq debootstrap xorriso isolinux squashfs-tools \
    grub-pc-bin grub-efi-amd64-bin mtools dosfstools rsync \
    live-build devscripts debhelper dpkg-dev

# Run the build
cd "$WSL_DIR"
bash scripts/build.sh

# Copy ISO back
cp -v iso/*.iso /mnt/c/Users/jaina/Desktop/
