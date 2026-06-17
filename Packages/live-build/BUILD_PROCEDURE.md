# EduOS ISO Build Procedure

## Prerequisites

- **OS**: Debian 13 (Trixie) or later (fresh install recommended)
- **Disk**: 10 GB free space
- **RAM**: 2 GB minimum
- **Packages**: `live-build`, `debootstrap`, `git`

## Step 1: Prepare Build Environment

```bash
# Install build dependencies
sudo apt-get update
sudo apt-get install -y live-build debootstrap git

# Clone EduOS repository
git clone https://github.com/your-org/eduos.git
cd eduos
```

## Step 2: Review Configuration

All build configuration is in `Packages/live-build/`:

| File | Purpose |
|---|---|
| `build-eduos-iso.sh` | Main build script (run this) |
| `packages-lock.txt` | Exact package versions from reference system |
| `packages-full-lock.txt` | All 3400+ packages including dependencies |

The build script automatically:
- Configures live-build for Debian Trixie
- Installs KDE Plasma desktop
- Adds all EduOS applications (ExamMode, AdminCenter, LearnHub, DevSuite, CyberLab)
- Includes EduOS branding (wallpaper, SDDM theme, Plymouth, color scheme)
- Creates default users (student, admin, exam)
- Configures UFW firewall
- Sets up KDE Plasma default settings

## Step 3: Build ISO

```bash
cd Packages/live-build
sudo ./build-eduos-iso.sh
```

Build time: ~30-60 minutes depending on network speed and CPU.

Output: `Packages/live-build/output/eduos-YYYYMMDD-amd64.iso`

## Step 4: Verify ISO

```bash
# Check ISO size (should be ~4-6 GB)
ls -lh output/eduos-*.iso

# Verify ISO in VirtualBox:
# 1. Create new VM (4 GB RAM, 2 CPU, 30 GB disk)
# 2. Attach the ISO
# 3. Boot live mode → verify everything works
# 4. Run installer → verify fresh installation
```

## Build Output

After a successful build, the ISO contains:

- **KDE Plasma 6.3.x** desktop with EduOS theme
- **Custom SDDM login** with glassmorphism design
- **Plymouth boot splash** with EduOS branding
- **Exam Mode**: Python/PyQt6 exam application with encrypted storage
- **Demo Exam**: 10-question showcase with PDF export
- **Admin Center**: Real-time system monitoring dashboard
- **Learn Hub**: Flask web portal (port 5050)
- **Dev Suite**: 12-tool development launcher grid
- **Cyber Lab**: 5 Docker-based security labs
- **Development tools**: GCC/G++ 14, Python 3.13, Java 21, Node.js 20, .NET SDK
- **Security tools**: Wireshark, Nmap, Hydra, John, SQLmap, Burp Suite, Docker
- **Office suite**: LibreOffice with KDE integration
- **Firewall**: UFW active with SSH allowed

## Troubleshooting

| Problem | Solution |
|---|---|
| `lb: command not found` | Install live-build: `apt install live-build` |
| ISO > 4.7 GB (FAT limit) | Use `--archive-areas` to exclude some firmware, or use ISO 9660 level 3 |
| Build fails on package X | Check `packages-lock.txt` — the package may have been removed from repos |
| Docker not in repos | Add Docker's official apt repository |
| Slow build | Use a local apt cache or Debian mirror |

## Reproducible Builds

To ensure bit-identical rebuilds:

1. Use the same `lb config` arguments
2. Pin all package versions via `packages-lock.txt`
3. Use the same `live-build` version
4. Use the same Debian snapshot mirror

```bash
lb config --mirror-bootstrap "http://snapshot.debian.org/archive/debian/YYYYMMDD/"
```

## CI/CD Integration

```yaml
# .github/workflows/build-iso.yml (example)
name: Build EduOS ISO
on:
  push:
    tags: ['v*']
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: sudo apt-get install -y live-build debootstrap
      - name: Build ISO
        run: sudo ./Packages/live-build/build-eduos-iso.sh
      - name: Upload ISO
        uses: actions/upload-artifact@v4
        with:
          name: eduos-iso
          path: Packages/live-build/output/*.iso
```
