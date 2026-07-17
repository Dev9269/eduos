# EduOS v3.0 Build Guide

> Version 3.0 | July 2026

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Build Environment Setup](#build-environment-setup)
3. [Dependencies](#dependencies)
4. [Clone Repository](#clone-repository)
5. [Build ISO Using live-build](#build-iso-using-live-build)
6. [Build Individual .deb Packages](#build-individual-deb-packages)
7. [Customize the Build](#customize-the-build)
8. [Build Output](#build-output)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Minimum System Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Debian 13 "Trixie" (recommended) or Debian 12 "Bookworm" |
| **Disk Space** | 20 GB free (40 GB recommended) |
| **RAM** | 4 GB (8 GB recommended) |
| **CPU** | 2+ cores (4+ recommended) |
| **Internet** | Broadband connection for package downloads |
| **Architecture** | x86_64 only |

### Required Tools

- `bash` (>= 5.2)
- `git` (>= 2.40)
- `live-build` (>= 202408)
- `debootstrap` (>= 1.0.134)
- `dpkg-dev` (>= 1.22)
- `fakeroot` (>= 1.35)
- `xorriso` (>= 1.5.6)
- `gpg` (>= 2.2)

---

## Build Environment Setup

### 1. Ensure You Are on Debian 13

```bash
cat /etc/debian_version
# Expected: 13.0 or higher
```

### 2. Install Base Build Dependencies

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y \
    git \
    live-build \
    debootstrap \
    dpkg-dev \
    fakeroot \
    xorriso \
    gnupg2 \
    curl \
    wget \
    ca-certificates
```

---

## Dependencies

### Build Dependencies

Run the following to install all build dependencies:

```bash
sudo apt install -y \
    # live-build system
    live-build \
    debootstrap \
    squashfs-tools \
    isolinux \
    syslinux-utils \
    # Package building
    build-essential \
    devscripts \
    debhelper \
    dh-python \
    python3-all \
    python3-setuptools \
    python3-stdeb \
    # Python packages
    python3 \
    python3-pip \
    python3-venv \
    python3-aiohttp \
    python3-psutil \
    python3-systemd \
    python3-django \
    python3-djangorestframework \
    python3-psycopg2 \
    python3-redis \
    python3-docker \
    python3-apt \
    python3-jupyter \
    # Security
    openssl \
    gnupg2 \
    apparmor-profiles \
    wireguard-tools \
    iptables \
    # Dev tools
    gcc \
    g++ \
    make \
    nodejs \
    npm \
    openjdk-17-jdk \
    rustc \
    cargo \
    # Desktop
    plasma-desktop \
    plasma-workspace \
    sddm \
    plymouth \
    plymouth-themes \
    # Other
    docker-ce \
    docker-compose \
    chromium \
    git
```

---

## Clone Repository

```bash
git clone https://github.com/edos/edos.git
cd edos
```

### Repository Structure

```
edos/
├── scripts/
│   ├── build.sh              # Master build script
│   ├── build-iso.sh          # ISO build using live-build
│   ├── build-packages.sh     # Build all .deb packages
│   ├── build-package.sh      # Build individual .deb package
│   └── clean.sh              # Clean build artifacts
├── config/
│   ├── live-build/           # live-build configuration
│   │   ├── auto/             # Auto-config scripts
│   │   ├── hooks/            # Custom hooks (live-build)
│   │   ├── includes.binary/  # Binary stage includes
│   │   └── includes.chroot/  # Chroot stage includes
│   ├── packages/             # Package configurations
│   ├── branding/             # EduOS branding assets
│   └── secureboot/           # Secure Boot certificates
├── packages/                 # Source code for .deb packages
│   ├── edos-core/
│   ├── edos-security/
│   ├── edos-daemon/
│   ├── edos-admin-service/
│   ├── edos-exam-service/
│   ├── edos-update-service/
│   ├── edos-learn-hub/
│   ├── edos-cyber-lab/
│   ├── edos-dev-suite/
│   └── edos-ui-theme/
├── debian/                   # Debian packaging metadata
├── documentation/            # Project documentation
├── tests/                    # Test suites
└── CHANGELOG.md
```

---

## Build ISO Using live-build

### Quick Build

The fastest way to build the complete ISO:

```bash
bash scripts/build.sh
```

This single command runs the entire build pipeline:
1. Builds all .deb packages
2. Configures live-build
3. Generates the ISO

### Step-by-Step ISO Build

If you prefer to run each stage manually:

#### 1. Configure live-build

```bash
cd config/live-build

lb config \
    --distribution trixie \
    --debian-installer false \
    --archive-areas "main contrib non-free non-free-firmware" \
    --bootappend-live "boot=live components quiet splash" \
    --iso-application "EduOS v3.0" \
    --iso-preparer "EduOS Team" \
    --iso-publisher "EduOS" \
    --iso-volume "EduOS v3.0" \
    --memtest none \
    --binary-images iso-hybrid \
    --syslinux-timeout 10
```

#### 2. Add Package Lists

Create package list files under `config/package-lists/`:

```bash
# config/package-lists/edos-core.list.chroot
edos-core
edos-security
edos-daemon
edos-admin-service
edos-exam-service
edos-update-service
edos-learn-hub
edos-cyber-lab
edos-dev-suite
edos-ui-theme
```

#### 3. Include EduOS Packages

Copy built .deb packages to `config/packages.chroot/`:

```bash
mkdir -p config/packages.chroot
cp ../../packages/*/dist/*.deb config/packages.chroot/
```

#### 4. Add Custom Hooks

Place hooks in `config/hooks/`:

```bash
# config/hooks/99-edos-setup.hook.chroot
#!/bin/bash

# Enable EduOS services
systemctl enable edos-daemon
systemctl enable edos-exam-daemon
systemctl enable edos-update-daemon
systemctl enable edos-sync-daemon

# Set default display manager
/usr/sbin/dmctl set-default sddm

# Configure EduOS branding
cp /usr/share/edos/branding/plymouth/ /usr/share/plymouth/themes/ -r
plymouth-set-default-theme edos

# Set EduOS wallpaper
cp /usr/share/edos/branding/wallpaper.jpg \
    /usr/share/wallpapers/EduOS/contents/images/
```

#### 5. Build the ISO

```bash
cd config/live-build
sudo lb build 2>&1 | tee build.log
```

The output ISO will be at `config/live-build/live-image-amd64.hybrid.iso`.

---

## Build Individual .deb Packages

### Build All Packages

```bash
bash scripts/build-packages.sh
```

### Build a Single Package

```bash
bash scripts/build-package.sh <package-name>
```

Example:

```bash
bash scripts/build-package.sh edos-daemon
```

### Package Build Output

Each built package is placed in its respective `dist/` directory:

```
packages/edos-core/dist/edos-core_3.0.0_all.deb
packages/edos-daemon/dist/edos-daemon_3.0.0_all.deb
packages/edos-security/dist/edos-security_3.0.0_all.deb
...
```

### Manual Package Build (Using dpkg-buildpackage)

```bash
cd packages/edos-daemon
dpkg-buildpackage -us -uc -b
```

---

## Customize the Build

### Adding Custom Software

1. Add the package name to the appropriate list in `config/package-lists/`
2. If needed, create a hook in `config/hooks/` for post-install configuration

### Modifying Branding

```
config/branding/
├── grub/
│   ├── grub-background.png     # GRUB boot screen background
│   └── grub-theme.txt          # GRUB theme configuration
├── plymouth/
│   ├── logo.png                # Plymouth boot splash logo
│   ├── progress-bar.png        # Boot progress bar
│   └── edos.script             # Plymouth animation script
├── sddm/
│   ├── sddm-theme.tar.gz       # SDDM login theme
│   └── sddm.conf               # SDDM configuration
├── wallpaper.jpg               # Default desktop wallpaper
├── logo.svg                    # EduOS logo (vector)
└── icon.png                    # Application icon
```

### Changing Default Applications

Edit `config/includes.chroot/usr/share/edos/defaults/`:

```
defaults/
├── applications.json           # Default app associations
├── bookmarks.html              # Default browser bookmarks
├── plasma-settings.tar.gz      # KDE Plasma configuration
└── sddm.conf                   # Login manager settings
```

### Secure Boot Configuration

```bash
# Generate Secure Boot certificates
scripts/generate-secureboot-certs.sh

# Place certificates
config/secureboot/
├── DB.key                      # Signature key
├── DB.crt                      # Signature certificate
├── KEK.key                     # Key Exchange Key
├── KEK.crt                     # Key Exchange Key certificate
└── PK.key                      # Platform Key
```

---

## Build Output

After a successful build, the following artifacts are produced:

```
edos/
├── build/
│   └── EduOS-v3.0.iso          # Bootable hybrid ISO (~4 GB)
├── packages/
│   └── <package>/
│       └── dist/
│           └── <package>.deb    # Individual .deb packages
└── build.log                    # Build log
```

### ISO Verification

```bash
# Verify ISO checksum
sha256sum build/EduOS-v3.0.iso

# Verify GPG signature
gpg --verify build/EduOS-v3.0.iso.sig build/EduOS-v3.0.iso
```

---

## Troubleshooting

### Common Issues

#### `live-build` fails with "No such file or directory"

Ensure all required tools are installed:

```bash
sudo apt install --reinstall live-build debootstrap
```

#### Package build fails with unmet dependencies

Install missing build dependencies:

```bash
sudo apt build-dep ./packages/<package-name>
```

#### ISO build fails due to disk space

Check available space and clean build artifacts:

```bash
bash scripts/clean.sh
df -h
```

#### GPG signing fails

Ensure your GPG key is set up:

```bash
gpg --list-keys
# If no key exists, generate one:
gpg --full-generate-key
```

#### Network timeouts during build

Use a local mirror:

```bash
lb config --mirror-bootstrap "http://deb.debian.org/debian/" \
          --mirror-chroot "http://deb.debian.org/debian/" \
          --mirror-binary "http://deb.debian.org/debian/"
```

#### QEMU test fails to boot

Enable KVM for better performance:

```bash
sudo apt install qemu-system-x86 qemu-kvm
sudo kvm -m 4096 -cdrom build/EduOS-v3.0.iso -accel kvm
```

### Build Logs

Build logs are written to `build.log` in the project root. For detailed debugging:

```bash
# ISO build debug
sudo lb build --debug 2>&1 | tee build-debug.log

# Package build debug
bash scripts/build-package.sh --debug <package-name>
```

### Clean Build

To perform a completely clean build:

```bash
bash scripts/clean.sh          # Clean build artifacts
rm -rf config/live-build/      # Reset live-build configuration
git checkout -- config/        # Restore default configuration
```

### Support

- **Documentation**: Refer to the `documentation/` directory
- **Issues**: https://github.com/edos/edos/issues
- **Discussions**: https://github.com/edos/edos/discussions

---

*Happy building! — The EduOS Team*
