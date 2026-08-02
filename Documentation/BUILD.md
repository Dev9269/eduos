# EduOS v3.0 Build Guide

> Version 3.0 | July 2026

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Build Environment Setup](#build-environment-setup)
3. [Repository Structure](#repository-structure)
4. [Validate the Build](#validate-the-build)
5. [Build the FreeBSD ISO](#build-the-freebsd-iso)
6. [Build Packages Manually](#build-packages-manually)
7. [Customize the Build](#customize-the-build)
8. [Build Output](#build-output)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Minimum System Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | FreeBSD 14.x (recommended) or Linux x86_64 |
| **Disk Space** | 20 GB free (40 GB recommended) |
| **RAM** | 4 GB (8 GB recommended) |
| **CPU** | 2+ cores (4+ recommended) |
| **Internet** | Broadband connection for package downloads |
| **Architecture** | x86_64 only |

### Required Tools

- `bash` (>= 5.2)
- `git` (>= 2.40)
- `python3` (>= 3.11) with `pytest` and `pyyaml`
- `xorriso` (>= 1.5.6)
- `curl` / `wget`
- `qemu-system-x86` (optional — for boot verification)

On FreeBSD, install the toolchain with:

```sh
pkg install -y bash git python311 py311-pip py311-pytest xorriso curl qemu
```

On Linux (for running the GitHub Actions build locally):

```sh
sudo apt install -y xorriso qemu-system-x86 curl wget python3 python3-pip
```

---

## Build Environment Setup

EduOS is built on **FreeBSD 14.x**. The base system is assembled from the
official FreeBSD `base.txz` and `kernel.txz` release archives, then layered
with the EduOS modules in `Packages/` and the first-boot configuration in
`Services/freebsd/`.

There are two supported build paths:

| Path | When to use |
|------|-------------|
| **GitHub Actions** (recommended) | Reproducible CI build; produces the ISO artifact automatically |
| **`Scripts/build.sh`** (local) | Quick local validation + package staging |

---

## Repository Structure

```
eduos/
├── Scripts/
│   ├── build.sh              # Master build orchestrator (validate + package)
│   ├── build-iso.sh          # ISO build entrypoint (points at CI workflow)
│   ├── install-eduos.sh      # Runtime installer (FreeBSD rc.d / Linux systemd)
│   ├── freebsd-pkg-cache.sh  # Offline package cache builder
│   └── eduos-welcome.py      # First-login welcome wizard
├── Packages/
│   ├── freebsd-packages.txt  # pkg(8) manifest for the base system
│   ├── eduos-server/         # Server modules (usr/lib/edos/server/)
│   ├── eduos-exam/           # ExamMode modules (usr/lib/edos/apps/exam/)
│   ├── eduos-devsuite/       # DevSuite modules (usr/lib/edos/apps/devsuite/)
│   └── ...                   # One directory per installable module
├── Services/
│   └── freebsd/              # rc.d service scripts + FreeBSD installer
│       ├── eduos_agent       # Agent service (rc.d)
│       ├── eduos_exam        # Exam daemon (rc.d)
│       └── install-agent-freebsd.sh
├── Server/                   # Central EduOS server (FastAPI)
├── AdminCenter/              # Administrator console
├── ExamMode/                 # Exam proctoring application
├── LearnHub/                 # Learning management web app
├── CyberLab/                 # Cyber-lab environments
├── DevSuite/                 # Development suite
├── InstitutionManager/       # Institution management
├── EcosystemDashboard/       # Ecosystem monitoring
├── Branding/                 # EduOS branding assets
├── Themes/                   # Desktop themes
├── Tests/                    # Test suites
└── .github/workflows/
    ├── build-freebsd-iso.yml # ISO build workflow (FreeBSD 14.x)
    └── ci.yml                # Lint + test + FreeBSD package validation
```

---

## Validate the Build

Run the full validation suite locally before building:

```bash
make validate
```

This runs, in order:

1. The pytest suite (`pytest tests/ -q`) — all tests must pass
2. `py_compile` over every Python file in the repository
3. YAML validation of `.github/workflows/*.yml`
4. Shell syntax checks on `Scripts/*.sh` and `Services/freebsd/*`
5. FreeBSD package-list validation (`Packages/freebsd-packages.txt`)

You can run individual checks with `make test`, `make lint`, and
`make clean`.

---

## Build the FreeBSD ISO

### Quick Build (recommended)

The ISO is built by the **Build EduOS FreeBSD ISO** workflow on GitHub
Actions (`build-freebsd-iso.yml`). To trigger it:

```bash
gh workflow run build-freebsd-iso.yml
```

The workflow runs on `ubuntu-24.04` and:

1. Downloads the FreeBSD 14.x base + kernel (`base.txz`, `kernel.txz`)
2. Extracts them into a `rootfs/`
3. Copies the EduOS modules (`AdminCenter`, `CyberLab`, `DevSuite`,
   `ExamMode`, `LearnHub`, `Scripts`, `Branding`, `Themes`, `Server`,
   `Services`) into `/opt/eduos`
4. Writes runtime config: `rc.conf` (hostname, dhcp, firstboot + agent
   rc.d entries), `boot/loader.conf`, `etc/fstab`, `etc/eduos/agent.conf`
5. Stages first-boot rc.d scripts: `eduos_firstboot` (pkg install
   python311 + pip packages) and `eduos_adduser` (creates the `student`
   user), plus the welcome autostart entry
6. Bundles an offline pip wheel cache into `/opt/eduos-packages/` with a
   matching `install-offline.sh`
7. Assembles the ISO with `xorriso` (mkisofs mode) and uploads it as a
   build artifact (`eduos-freebsd.iso`, 30-day retention)

### Local Build

The local entrypoint is `Scripts/build-iso.sh`:

```bash
bash Scripts/build-iso.sh
```

It performs local validation, then prints the instructions for triggering
the ISO build on GitHub Actions. The full local pipeline is:

```bash
bash Scripts/build.sh
```

which runs the tests, compiles all modules, stages the package tree into
`dist/`, and then either triggers the CI ISO build or prints the manual
instructions.

---

## Build Packages Manually

EduOS modules ship as FreeBSD-friendly directory trees under `Packages/`.
Each package follows the layout:

```
Packages/eduos-<module>/
└── usr/lib/edos/apps/<module>/   # Python modules installed to the system
```

Staging a module for distribution:

```bash
bash Scripts/build.sh            # stages all modules into dist/
ls dist/                         # staged package trees
```

There is no `dpkg-buildpackage` equivalent — FreeBSD modules are plain
directory installs. On the target machine, the module trees are copied
into `/usr/local/lib/edos/` (or `/usr/lib/edos/` on the ISO rootfs) and
enabled through the rc.d services in `Services/freebsd/`.

### Build a Single Module

```bash
python3 -m compileall -q Packages/eduos-server/
```

### Package Manifest

The complete list of FreeBSD `pkg(8)` packages installed on the base
system lives in `Packages/freebsd-packages.txt`. The first-boot script
installs the core runtime packages:

```sh
pkg install -y python311 py311-pip git curl wget bash nano
pip3.11 install --quiet cryptography fastapi uvicorn pyjwt websockets psutil
```

For offline installation, `Scripts/freebsd-pkg-cache.sh` fetches the
package and wheel caches and generates an `install-offline.sh` that works
without internet access.

---

## Customize the Build

### Adding Custom Software

1. Add the package name to `Packages/freebsd-packages.txt`
2. For first-boot installs, add the package to the `pkg install` line in
   the `eduos_firstboot` rc.d script in `build-freebsd-iso.yml`
3. For Python modules, add the wheel to the offline cache in
   `Scripts/freebsd-pkg-cache.sh` (or to the `pip download` list in the
   workflow's "Bundle Python packages offline cache" step)

### Modifying Branding

Branding assets live in `Branding/`:

```
Branding/
├── autostart/
│   └── eduos-welcome.desktop   # First-login welcome autostart entry
├── wallpaper.jpg               # Default desktop wallpaper
├── logo.svg                    # EduOS logo (vector)
└── icon.png                    # Application icon
```

The welcome wizard (`Scripts/eduos-welcome.py`) is staged for the
`student` user during first boot via the desktop entry above.

### Changing First-Boot Behavior

First-boot behavior is defined by the rc.d scripts generated in
`build-freebsd-iso.yml`:

- `rootfs/etc/rc.d/eduos_firstboot` — package + service installation
- `rootfs/etc/rc.d/eduos_adduser` — `student` user creation

Both are `KEYWORD: firstboot` scripts — they run once, disable
themselves, and remove themselves from `/etc/rc.d/` on completion.

---

## Build Output

After a successful build, the following artifacts are produced:

```
eduos/
├── dist/                        # Staged module packages
│   ├── eduos-server/
│   ├── eduos-exam/
│   └── ...
├── eduos-freebsd.iso            # Bootable FreeBSD ISO (~4 GB, CI artifact)
└── build.log                    # Build log
```

### ISO Verification

```bash
# Verify ISO checksum
sha256sum eduos-freebsd.iso

# Verify ISO contents
xorriso -as mkisofs -indev eduos-freebsd.iso -find . -name loader.conf
```

### Boot Test with QEMU

```bash
# Download the artifact from GitHub Actions, then:
qemu-system-x86_64 \
  -m 4096 \
  -cdrom eduos-freebsd.iso \
  -boot d \
  -accel kvm \
  -netdev user,id=n1 -device e1000,netdev=n1
```

---

## Troubleshooting

### CI workflow fails at "Download FreeBSD base"

The FreeBSD release URLs change per release. Verify the current stable
release at https://download.freebsd.org/releases/amd64/ and update
`FREEBSD_VERSION` in `build-freebsd-iso.yml`.

### Local tests fail

Run the suite verbosely and check the module under test:

```bash
pytest tests/ -v --tb=short
```

The suite covers the server API (auth, rate limiting, SQL injection),
the coding engine sandbox, and the LearnHub sync flow.

### `xorriso` not found

Install it:

```sh
pkg install -y xorriso        # FreeBSD
sudo apt install xorriso      # Linux
```

### First boot fails at `pkg update`

The first-boot script uses `ASSUME_ALWAYS_YES=YES` and tolerates failures
(`|| true`) so the boot continues. For offline environments, generate the
package cache first:

```bash
bash Scripts/freebsd-pkg-cache.sh
```

and copy the resulting cache into `rootfs/opt/eduos-packages/` before the
ISO build step.

### QEMU test fails to boot

Enable KVM for better performance:

```bash
sudo apt install qemu-system-x86 qemu-kvm    # Linux
sudo kvm -m 4096 -cdrom eduos-freebsd.iso -accel kvm
```

---

## Build Logs

Build logs are written to `build.log` in the project root. For detailed
debugging:

```bash
# Local validation log
bash Scripts/build.sh 2>&1 | tee build.log

# CI run log
gh run view --log
```

### Clean Build

To perform a completely clean build:

```bash
make clean        # Remove dist/, build/, __pycache__ and .pytest_cache
git status        # Verify only expected files are left
```

---

### Support

- **Documentation**: Refer to the `Documentation/` directory
- **Issues**: https://github.com/edos/edos/issues
- **Discussions**: https://github.com/edos/edos/discussions

---

*Happy building! — The EduOS Team*
