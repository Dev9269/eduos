# EduOS v3.0 Developer Guide

> Version 3.0 | July 2026

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Creating New Applications](#creating-new-applications)
4. [Package Format](#package-format)
5. [Systemd Services](#systemd-services)
6. [Customizing Themes](#customizing-themes)
7. [Building from Source](#building-from-source)
8. [Contributing Guidelines](#contributing-guidelines)

---

## Getting Started

### Prerequisites

- **Debian 13 "Trixie"** (recommended) or Debian 12 "Bookworm"
- **Git** (>= 2.40)
- **Python 3.12+** (most EduOS services are Python-based)
- **Bash** (>= 5.2)
- **Docker** (for Cyber Lab development)

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/edos/edos.git
cd edos

# Install development dependencies
sudo apt install -y \
    git build-essential debhelper devscripts dh-python \
    python3-all python3-setuptools python3-stdeb \
    python3-pip python3-venv

# Create a Python virtual environment for development
python3 -m venv .venv
source .venv/bin/activate

# Install Python development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Development Workflow

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create a branch** for your feature or fix
4. **Make changes** following the coding standards
5. **Test** your changes
6. **Submit a pull request**

---

## Project Structure

```
edos/
├── packages/                        # Source for all .deb packages
│   ├── edos-core/                   # Core libraries and configuration
│   │   ├── debian/                  # Debian packaging metadata
│   │   ├── src/                     # Python source code
│   │   │   ├── edos/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py        # Configuration management
│   │   │   │   ├── constants.py     # System constants
│   │   │   │   ├── exceptions.py    # Custom exceptions
│   │   │   │   ├── logger.py        # Logging utilities
│   │   │   │   └── services.py      # Service registry
│   │   ├── tests/                   # Package tests
│   │   └── setup.py                 # Python package setup
│   │
│   ├── edos-security/               # Security services
│   │   ├── debian/
│   │   ├── src/
│   │   │   ├── edos/security/
│   │   │   │   ├── auth/            # Authentication
│   │   │   │   │   ├── authenticator.py
│   │   │   │   │   ├── role_manager.py
│   │   │   │   │   └── session_manager.py
│   │   │   │   ├── encryption/      # Cryptography
│   │   │   │   ├── audit/           # Audit logging
│   │   │   │   └── policy/          # Policy engine
│   │   ├── tests/
│   │   └── setup.py
│   │
│   ├── edos-daemon/                 # Core system daemon
│   │   ├── debian/
│   │   ├── src/
│   │   │   ├── edos/daemon/
│   │   │   │   ├── main.py          # Entry point
│   │   │   │   ├── api/             # REST API endpoints
│   │   │   │   ├── handlers/        # Event handlers
│   │   │   │   └── monitors/        # System monitors
│   │   ├── tests/
│   │   └── setup.py
│   │
│   ├── edos-admin-service/          # Admin backend API
│   │   ├── debian/
│   │   ├── src/                     # Django application
│   │   ├── tests/
│   │   └── setup.py
│   │
│   ├── edos-exam-service/           # Exam management
│   │   ├── debian/
│   │   ├── src/
│   │   ├── tests/
│   │   └── setup.py
│   │
│   ├── edos-update-service/          # Update management
│   │   ├── debian/
│   │   ├── src/
│   │   ├── tests/
│   │   └── setup.py
│   │
│   ├── edos-learn-hub/              # Learning management
│   │   ├── debian/
│   │   ├── src/                     # Django application
│   │   ├── tests/
│   │   └── setup.py
│   │
│   ├── edos-cyber-lab/              # Cybersecurity lab
│   │   ├── debian/
│   │   ├── src/
│   │   ├── docker/                  # Docker scenarios
│   │   ├── tests/
│   │   └── setup.py
│   │
│   ├── edos-dev-suite/              # Development tools
│   │   ├── debian/
│   │   ├── src/
│   │   ├── tests/
│   │   └── setup.py
│   │
│   └── edos-ui-theme/               # Desktop theming
│       ├── debian/
│       ├── plasma/                  # Plasma theme files
│       ├── sddm/                    # Login screen theme
│       ├── plymouth/                # Boot splash theme
│       ├── grub/                    # GRUB theme
│       ├── wallpapers/              # Desktop wallpapers
│       └── icons/                   # Application icons
│
├── config/                          # Build configuration
│   ├── live-build/                  # live-build configuration
│   │   ├── auto/
│   │   ├── hooks/
│   │   ├── includes.chroot/
│   │   └── includes.binary/
│   ├── branding/                    # Branding assets
│   ├── secureboot/                  # Secure Boot certificates
│   └── packages/                    # Package config overrides
│
├── scripts/                         # Build and utility scripts
│   ├── build.sh                     # Master build script
│   ├── build-iso.sh                 # ISO generation
│   ├── build-packages.sh            # Build all packages
│   ├── build-package.sh             # Build single package
│   ├── clean.sh                     # Clean artifacts
│   ├── generate-secureboot-certs.sh
│   └── release.sh                   # Release automation
│
├── tests/                           # Integration/system tests
│   ├── unit/
│   ├── integration/
│   ├── performance/
│   └── security/
│
├── documentation/                   # Project documentation
│
├── .github/                         # GitHub CI/CD configuration
│   ├── workflows/
│   │   ├── build.yml
│   │   ├── test.yml
│   │   └── release.yml
│   └── CONTRIBUTING.md
│
├── README.md
├── CHANGELOG.md
└── LICENSE
```

---

## Creating New Applications

### Step 1: Create the Package Skeleton

```bash
# Use the scaffolding script
bash scripts/create-package.sh my-new-app

# Or create manually
mkdir -p packages/edos-my-new-app/{debian,src/edos/my_new_app,tests}
```

### Step 2: Package Structure

Every EduOS package follows a standard structure:

```
packages/edos-my-new-app/
├── debian/
│   ├── changelog                  # Package changelog
│   ├── compat                     # Debhelper compatibility level
│   ├── control                    # Package metadata and dependencies
│   ├── copyright                  # Licensing information
│   ├── rules                      # Build rules (Makefile)
│   ├── install                    # File installation rules
│   ├── edos-my-new-app.service    # systemd service (if applicable)
│   └── edos-my-new-app.postinst   # Post-installation script
├── src/
│   └── edos/
│       └── my_new_app/
│           ├── __init__.py
│           ├── main.py            # Application entry point
│           └── ...
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── setup.py                       # Python package setup
└── README.md                      # Package-specific documentation
```

### Step 3: Define Package Metadata

**debian/control**:

```
Source: edos-my-new-app
Section: education
Priority: optional
Maintainer: EduOS Team <team@edos.edu>
Build-Depends: debhelper-compat (= 13), dh-python, python3-all
Standards-Version: 4.6.2

Package: edos-my-new-app
Architecture: all
Depends: ${python3:Depends}, ${misc:Depends}, edos-core
Description: My New EduOS Application
 A description of the new application and its functionality.
```

### Step 4: Implement the Application

```python
# src/edos/my_new_app/main.py
import logging
from edos.core.config import Config
from edos.core.logger import setup_logging

logger = logging.getLogger(__name__)

class MyNewApp:
    def __init__(self, config: Config):
        self.config = config
        logger.info("MyNewApp initialized")

    def run(self):
        logger.info("MyNewApp starting")
        # Application logic here
        pass

def main():
    config = Config.load()
    setup_logging(config)
    app = MyNewApp(config)
    app.run()

if __name__ == "__main__":
    main()
```

### Step 5: Write Tests

```python
# tests/test_main.py
import pytest
from edos.my_new_app.main import MyNewApp

def test_app_initialization():
    app = MyNewApp(config={"test": True})
    assert app is not None
```

### Step 6: Build and Test

```bash
# Build the package
bash scripts/build-package.sh edos-my-new-app

# Install for testing
sudo dpkg -i packages/edos-my-new-app/dist/edos-my-new-app_*.deb

# Run tests
cd packages/edos-my-new-app
python3 -m pytest tests/
```

### Step 7: Integrate into ISO Build

Add the package to `config/package-lists/edos-core.list.chroot`:

```
edos-my-new-app
```

---

## Package Format

EduOS uses standard Debian `.deb` packages. Each package is built using `debhelper` and `dh-python`.

### Package Naming Convention

```
edos-<component>_<version>_<architecture>.deb

Examples:
edos-daemon_3.0.0_all.deb
edos-security_3.0.0_all.deb
edos-ui-theme_3.0.0_all.deb
```

### Version Scheme

```
<major>.<minor>.<patch>[-<pre-release>]

3.0.0          # Stable release
3.1.0-beta1    # Beta pre-release
3.1.0-alpha1   # Alpha pre-release
```

### Required Package Fields

| Field | Description |
|-------|-------------|
| `Package` | Package name (edos-<component>) |
| `Version` | Semantic version |
| `Architecture` | all (Python) or amd64 (compiled) |
| `Maintainer` | EduOS Team <team@edos.edu> |
| `Description` | Single-line summary |
| `Depends` | Runtime dependencies |
| `Recommends` | Optional dependencies |
| `Section` | `education` |

### Python Packaging (setup.py)

```python
from setuptools import setup, find_packages

setup(
    name="edos-my-new-app",
    version="3.0.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "edos-core>=3.0.0",
        "aiohttp>=3.9",
        "pydantic>=2.0",
    ],
    entry_points={
        "console_scripts": [
            "edos-my-new-app=edos.my_new_app.main:main",
        ],
    },
)
```

---

## Systemd Services

Every long-running EduOS component runs as a systemd service.

### Service File Template

```
[Unit]
Description=EduOS My New App Service
Documentation=https://docs.edos.edu
Wants=network.target
After=network.target edos-daemon.service

[Service]
Type=simple
User=edos
Group=edos
ExecStart=/usr/bin/edos-my-new-app
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

# Security hardening
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
NoNewPrivileges=true
CapabilityBoundingSet=
MemoryMax=256M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
```

### Service Lifecycle

```bash
# Install service
sudo systemctl daemon-reload
sudo systemctl enable edos-my-new-app.service

# Start/Stop/Restart
sudo systemctl start edos-my-new-app.service
sudo systemctl stop edos-my-new-app.service
sudo systemctl restart edos-my-new-app.service

# View status
sudo systemctl status edos-my-new-app.service

# View logs
sudo journalctl -u edos-my-new-app.service -f

# Reload configuration
sudo systemctl reload edos-my-new-app.service
```

### Logging

All EduOS services write logs to systemd journal:

```python
import logging
import systemd.journal

logger = logging.getLogger(__name__)
handler = systemd.journal.JournalHandler()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Health Check Endpoint

Each HTTP service should expose a `/health` endpoint:

```python
# Return 200 OK with service status
{
    "service": "edos-my-new-app",
    "version": "3.0.0",
    "status": "healthy",
    "uptime": 3600,
    "dependencies": {
        "postgresql": "connected",
        "redis": "connected"
    }
}
```

---

## Customizing Themes

### Desktop Theme (Plasma)

EduOS uses a custom KDE Plasma theme with a glassmorphism design.

#### Theme Location

```
/usr/share/plasma/desktoptheme/edos/
├── metadata.desktop
├── colors
├── wallpapers/
├── widgets/
└── dialogs/
```

#### Customization

```bash
# Edit the color scheme
nano /usr/share/plasma/desktoptheme/edos/colors

# Replace wallpaper
sudo cp my-wallpaper.jpg /usr/share/wallpapers/EduOS/contents/images/

# Apply theme globally
kwriteconfig5 --file ~/.config/plasmarc --group Theme --key name "edos"
```

### Login Screen (SDDM)

```
/usr/share/sddm/themes/edos/
├── theme.conf
├── Main.qml
├── background.jpg
└── components/
```

### Boot Splash (Plymouth)

```
/usr/share/plymouth/themes/edos/
├── edos.plymouth
├── logo.png
├── progress-bar.png
├── bullet.png
├── box.png
├── entry.png
└── lock.png
```

### Bootloader (GRUB)

```
/boot/grub/themes/edos/
├── theme.txt
├── icons/
├── background.png
└── fonts/
```

#### Building Theme Packages

```bash
# The edos-ui-theme package bundles all theme components
cd packages/edos-ui-theme

# Modify theme files in the source directory
# Rebuild the package
dpkg-buildpackage -us -uc -b
```

---

## Building from Source

See the [BUILD.md](./BUILD.md) guide for detailed build instructions.

### Quick Build

```bash
git clone https://github.com/edos/edos.git
cd edos
bash scripts/build.sh
```

### Development Build

```bash
# Build packages only (no ISO)
bash scripts/build-packages.sh

# Install built packages locally
sudo dpkg -i packages/*/dist/*.deb

# Run in development mode
cd packages/edos-daemon
python3 -m edos.daemon.main --dev --config /etc/edos/daemon.conf
```

---

## Contributing Guidelines

### Code of Conduct

All contributors must adhere to the [EduOS Code of Conduct](https://github.com/edos/edos/blob/main/.github/CODE_OF_CONDUCT.md). We strive to maintain a welcoming and inclusive community.

### Coding Standards

#### Python

- Follow **PEP 8** style guide
- Use **type hints** for all function signatures
- Maximum line length: **100 characters**
- Use **f-strings** for string formatting
- Use **pathlib** for filesystem paths
- Write **docstrings** for all public APIs (Google style)

```python
from pathlib import Path
from typing import Optional


def process_exam(
    exam_id: str,
    user_id: str,
    duration: int,
    config_path: Optional[Path] = None
) -> dict:
    """Process an exam submission.

    Args:
        exam_id: Unique identifier for the exam.
        user_id: Unique identifier for the user.
        duration: Exam duration in minutes.
        config_path: Optional path to configuration file.

    Returns:
        A dictionary containing exam results.

    Raises:
        ExamNotFoundError: If exam_id does not exist.
    """
    ...
```

#### Bash

- Use `#!/bin/bash` shebang
- Enable strict mode: `set -euo pipefail`
- Use functions for reusable logic
- Quote all variable expansions

```bash
#!/bin/bash
set -euo pipefail

build_package() {
    local package_name="$1"
    echo "Building ${package_name}..."
    cd "packages/${package_name}"
    dpkg-buildpackage -us -uc -b
}
```

#### Git Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`

Examples:
```
feat(daemon): add health check endpoint
fix(exam): resolve timeout on large question banks
docs(arch): update database schema documentation
test(security): add unit tests for RBAC enforcement
```

### Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add a changelog entry in `CHANGELOG.md`
4. Request review from at least one maintainer
5. Squash commits before merging

### Testing Requirements

- **Unit tests**: Required for all new code
- **Integration tests**: Required for service interactions
- **Coverage**: Minimum 80% code coverage

### Branch Strategy

```
main              # Stable, production-ready code
develop           # Integration branch for features
feature/*         # New features (branch from develop)
fix/*             # Bug fixes (branch from develop)
release/*         # Release preparation (branch from develop)
```

---

## API Documentation

Each EduOS service provides a REST API. See the service-specific documentation for endpoint details.

| Service | Base URL | Documentation |
|---------|----------|---------------|
| Core Daemon | `http://localhost:8080` | [docs/edos-daemon-api.md](https://docs.edos.edu/api/daemon) |
| Admin Service | `http://localhost:8081` | [docs/edos-admin-api.md](https://docs.edos.edu/api/admin) |
| Exam Service | `http://localhost:8082` | [docs/edos-exam-api.md](https://docs.edos.edu/api/exam) |
| Learn Hub | `http://localhost:8083` | [docs/edos-learn-api.md](https://docs.edos.edu/api/learn) |

---

*Thank you for contributing to EduOS! — The EduOS Team*
