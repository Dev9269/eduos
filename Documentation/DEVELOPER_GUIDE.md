# EduOS v3.0 Developer Guide

> Version 3.0 | July 2026

---

## FreeBSD Development Setup

### Install FreeBSD 14.2
Download from https://download.freebsd.org/releases/amd64/14.2-RELEASE/

### Install dependencies
```sh
pkg install python311 py311-pip kde5 sddm git
pip3.11 install -r /opt/eduos/requirements.txt
```

### Run EduOS on FreeBSD
```sh
sh /opt/eduos/Scripts/freebsd-desktop-setup.sh
```

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Creating New Applications](#creating-new-applications)
4. [Package Format](#package-format)
5. [FreeBSD rc.d Services](#freebsd-rc.d-services)
6. [Customizing Themes](#customizing-themes)
7. [Building from Source](#building-from-source)
8. [Contributing Guidelines](#contributing-guidelines)

---

## Getting Started

### Prerequisites

- **FreeBSD 14.2** (recommended) or FreeBSD 14.1 (dev in WSL/Linux also works)
- **Git** (>= 2.40)
- **Python 3.11+** (most EduOS services are Python-based)
- **Bash** (>= 5.2)
- **Podman** (for Cyber Lab development)

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/edos/edos.git
cd edos

# Install development dependencies (FreeBSD)
sudo pkg install -y \
    git python311 py311-pip py311-pytest \
    bash py311-fastapi py311-uvicorn

# Create a Python virtual environment for development
python3 -m venv .venv
source .venv/bin/activate

# Install Python development dependencies
pip install -r requirements.txt

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
├── Packages/                         # Installable module trees
│   ├── eduos-server/                 # Server modules (usr/lib/edos/server/)
│   ├── eduos-exam/                   # ExamMode modules (usr/lib/edos/apps/exam/)
│   ├── eduos-services/               # Service daemons (usr/lib/edos/services/)
│   │   ├── freebsd/                  # rc.d units for all daemons
│   │   └── lib/systemd/              # Legacy Linux units
│   ├── eduos-devsuite/               # DevSuite modules
│   ├── eduos-settings/               # Settings app
│   └── freebsd-packages.txt          # pkg(8) base manifest
│
├── Server/                           # Central EduOS server (FastAPI)
├── AdminCenter/                      # Administrator console (PyQt6)
├── ExamMode/                         # Exam proctoring app (PyQt6)
├── LearnHub/                         # Learning management web app
├── CyberLab/                         # Cyber-lab environments
├── DevSuite/                         # Development suite
├── InstitutionManager/               # Institution management
├── EcosystemDashboard/               # Ecosystem monitoring
├── Services/                         # Runtime services
│   └── freebsd/                      # Agent + exam rc.d units, installer
├── Scripts/                          # Build and utility scripts
│   ├── build.sh                      # Master build orchestrator
│   ├── build-iso.sh                  # ISO build entrypoint (CI)
│   ├── freebsd-pkg-cache.sh          # Offline package cache builder
│   ├── test-freebsd-iso.sh           # QEMU boot test
│   ├── install-eduos.sh              # Runtime installer
│   └── eduos-welcome.py              # First-login wizard
├── Branding/                         # Branding assets
├── Themes/                           # Desktop themes
│
├── tests/                            # Pytest suites
│   ├── test_server.py                # Package server API tests
│   ├── test_security.py              # Security regression tests
│   ├── test_coding_engine.py         # Sandbox tests
│   ├── test_exam_flow.py             # End-to-end exam lifecycle
│   ├── test_health.py                # Health monitoring tests
│   └── test_daemons.py               # Daemon correctness tests
│
├── Documentation/                    # Project documentation
├── .github/workflows/                # CI/CD configuration
│   ├── ci.yml                        # Lint + test + FreeBSD validation
│   └── build-freebsd-iso.yml         # FreeBSD ISO build
├── README.md
├── CHANGELOG.md
└── LICENSE
```

---

## Creating New Applications

### Step 1: Create the Package Skeleton

```bash
# Create the module directory
mkdir -p Packages/edos-my-new-app/usr/lib/edos/apps/my_new_app/tests
```

### Step 2: Package Structure

Every EduOS package follows a standard structure:

```
Packages/edos-my-new-app/
├── freebsd-packages.txt            # pkg(8) manifest entries (optional)
├── usr/
│   └── lib/
│       └── edos/
│           └── apps/
│               └── my_new_app/
│                   ├── __init__.py
│                   ├── main.py            # Application entry point
│                   └── ...
├── lib/systemd/                    # Linux systemd units (optional, legacy)
├── freebsd/                        # FreeBSD rc.d services (optional)
│   ├── eduos_my_new_app
│   └── install.sh
├── tests/
│   ├── __init__.py
│   └── test_main.py
└── README.md                      # Package-specific documentation
```

### Step 3: Define Package Metadata

**Packages/freebsd-packages.txt** (base-system manifest):

```
# EduOS runtime packages (installed by the first-boot script)
python311
py311-pip
git
```

**services manifest**: register the rc.d service in
`Packages/eduos-my-new-app/freebsd/eduos_my_new_app`:

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
# Compile-check the module
python3 -m py_compile Packages/edos-my-new-app/usr/lib/edos/apps/my_new_app/*.py

# Stage the module tree for distribution
bash Scripts/build.sh

# Run tests
python3 -m pytest Packages/edos-my-new-app/tests/
```

### Step 7: Integrate into ISO Build

Add the package to `Packages/freebsd-packages.txt` and copy the module
tree into the ISO rootfs (`rootfs/opt/eduos/`) via the
`build-freebsd-iso.yml` workflow's copy step.

---

## Package Format

EduOS ships modules as FreeBSD-friendly directory trees under `Packages/`.
Each module installs into `/usr/lib/edos/apps/<module>` on the ISO rootfs
(or `/usr/local/lib/edos/` on a pkg-based install), with optional rc.d
services in `Packages/<module>/freebsd/`.

### Package Naming Convention

```
Packages/edos-<component>/

Examples:
Packages/edos-server/
Packages/eduos-exam/
Packages/eduos-devsuite/
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
| `name` | Module name (eduos-<component>) |
| `version` | Semantic version |
| `server_url` | Campus server URL (ws://eduos-server.local:8765) |
| `token` | Agent auth token |
| `install` | Optional offline installer (`freebsd/install.sh`) |

### Python Module Layout

```python
# Packages/eduos-my-new-app/usr/lib/edos/apps/my_new_app/main.py
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class MyNewApp:
    def __init__(self, config: dict):
        self.config = config
        logger.info("MyNewApp initialized")

    def run(self):
        logger.info("MyNewApp starting")
        # Application logic here
        pass

def main():
    # Config from /etc/eduos/agent.conf or ~/.eduos/agent.conf
    app = MyNewApp({})
    app.run()

if __name__ == "__main__":
    main()
```

---

## FreeBSD rc.d Services

Every long-running EduOS component runs as an rc.d service on FreeBSD
(see `Packages/eduos-services/freebsd/` for the daemon set).

### Service File Template

```
#!/bin/sh
# PROVIDE: eduos_my_new_app
# REQUIRE: NETWORKING eduos_agent
# KEYWORD: shutdown

. /etc/rc.subr
name="eduos_my_new_app"
rcvar="eduos_my_new_app_enable"
command="/usr/local/bin/python3.11"
command_args="/opt/eduos/Packages/eduos-my-new-app/usr/lib/edos/apps/my_new_app/main.py"
pidfile="/var/run/${name}.pid"
logfile="/var/log/eduos-my-new-app.log"

start_cmd="${name}_start"
eduos_my_new_app_start() {
    /usr/sbin/daemon -p "$pidfile" -o "$logfile" -r \
        ${command} ${command_args}
    echo "EduOS My New App started"
}

load_rc_config $name
: ${eduos_my_new_app_enable:=YES}
run_rc_command "$1"
```

### Service Lifecycle

```sh
# Install service
sudo cp Packages/eduos-my-new-app/freebsd/eduos_my_new_app \
    /usr/local/etc/rc.d/
sudo chmod +x /usr/local/etc/rc.d/eduos_my_new_app

# Enable + Start/Stop/Restart
sudo sysrc eduos_my_new_app_enable=YES
sudo service eduos_my_new_app start
sudo service eduos_my_new_app stop
sudo service eduos_my_new_app restart

# View status
sudo service eduos_my_new_app status

# View logs
sudo tail -f /var/log/eduos-my-new-app.log
```

### Logging

All EduOS services write to syslog (and their own log file via
`/usr/sbin/daemon -o`):

```python
import syslog
syslog.openlog("eduos-my-new-app", syslog.LOG_PID, syslog.LOG_DAEMON)
syslog.syslog(syslog.LOG_INFO, "EduOS My New App started")
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

### Bootloader (FreeBSD loader)

```
/boot/loader.conf
├── geom_label_load="YES"
├── zfs_load="NO"
├── kern.vty=vt
├── autoboot_delay="3"
└── beastie_disable="YES"
```

#### Building Theme Packages

```bash
# Theme components live in Branding/ and Themes/
cd Themes

# Modify theme files, then stage with the build script
bash Scripts/build.sh
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
# Validate + stage modules (no ISO)
bash Scripts/build.sh

# Install modules locally
bash Scripts/install-eduos.sh

# Run in development mode
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

build_module() {
    local module_dir="$1"
    echo "Staging ${module_dir}..."
    python3 -m py_compile "${module_dir}"/usr/lib/edos/apps/*/*.py
    bash Scripts/build.sh
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
