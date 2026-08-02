<div align="center">

# 📚 EduOS

[![CI](https://github.com/Dev9269/eduos/actions/workflows/ci.yml/badge.svg)](https://github.com/Dev9269/eduos/actions/workflows/ci.yml)
[![Stars](https://img.shields.io/github/stars/Dev9269/eduos?style=flat-square&logo=github&color=gold)](https://github.com/Dev9269/eduos)
[![Forks](https://img.shields.io/github/forks/Dev9269/eduos?style=flat-square&logo=github&color=blue)](https://github.com/Dev9269/eduos/forks)
[![Last Commit](https://img.shields.io/github/last-commit/Dev9269/eduos?style=flat-square&color=blueviolet)](https://github.com/Dev9269/eduos/commits/main)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=flat-square)](LICENSE)
[![FreeBSD](https://img.shields.io/badge/FreeBSD-14.x-AB2B28?style=flat-square&logo=freebsd&logoColor=white)](https://freebsd.org)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-40%20passing-brightgreen?style=flat-square)](tests/)

**EduOS** is a Unix/FreeBSD-based educational operating system for Indian
engineering colleges — integrating secure exams, learning tools, dev
environments, cyber labs, and centralized campus administration.

**Created by** [Jainam Maru](https://github.com/Dev9269) — B.Tech Cybersecurity, Parul University

</div>

---

## Why FreeBSD?

EduOS is built on **FreeBSD 14.x** — not Linux. This is a deliberate
architectural decision:

| Factor | Linux (GPL v2) | FreeBSD (BSD License) |
|---|---|---|
| Source disclosure | **Required** if distributed | **Not required** |
| Proprietary layers | Cannot be closed | Can be fully closed |
| Used by | Android, most servers | macOS, PlayStation, Nintendo Switch |

EduOS's exam security engine, admin management system, and agent
protocol are **proprietary components** that require a BSD license base.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│            Admin Laptop (2-5 devices)               │
│         PyQt6 Admin Panel + Server Token            │
└────────────────────┬────────────────────────────────┘
                     │ WebSocket (campus LAN)
                     ▼
┌─────────────────────────────────────────────────────┐
│          EduOS Server (gaming laptop)               │
│    FastAPI + SQLite + JWT Auth + Scheduler          │
└────────────────────┬────────────────────────────────┘
                     │ WebSocket (campus LAN)
                     ▼
┌─────────────────────────────────────────────────────┐
│          Student PCs (EduOS FreeBSD)                │
│   Agent Daemon + Exam Mode + Learn Hub + CyberLab  │
└─────────────────────────────────────────────────────┘
```

## Modules

| Module | Description | Status |
|---|---|---|
| 🖥 **AdminCenter** | Centralized device management, exam control | ✅ Active |
| 📝 **ExamMode** | Secure lockdown exam environment | ✅ Active |
| 📚 **LearnHub** | Student learning portal (Flask) | ✅ Active |
| 💻 **DevSuite** | Programming tools launcher | ✅ Active |
| 🔐 **CyberLab** | Isolated cybersecurity practice | ✅ Active |
| 🏫 **InstitutionManager** | Multi-institution admin dashboard | ✅ Active |
| 🌐 **EcosystemDashboard** | System-wide analytics | ✅ Active |
| 🤖 **Server** | FastAPI backend with JWT auth | ✅ Active |
| 👁 **Agent** | FreeBSD rc.d daemon on student PCs | ✅ Active |

---

## 📑 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [System Users](#-system-users)
- [Architecture](#-architecture)
- [Security](#-security)
- [Project Structure](#-project-structure)
- [Pre-installed Tools](#-pre-installed-development-tools)
- [Available Scripts](#-available-scripts-scripts)
- [License](#-license)

---

## 📥 Installation

### On FreeBSD 14.x (Target Platform)
```sh
# 1. Clone repo
git clone https://github.com/Dev9269/eduos.git /opt/eduos

# 2. Run desktop setup
sh /opt/eduos/Scripts/freebsd-desktop-setup.sh

# 3. Start the server (on admin laptop)
bash /opt/eduos/Server/start-server.sh

# 4. Generate admin token
python3 /opt/eduos/Server/generate-admin-token.py
```

### For Development (any OS)
```bash
git clone https://github.com/Dev9269/eduos.git
cd eduos
pip install -r requirements.txt
pytest tests/ -v
```

---

## ⚡ Quick Start

```bash
eduos-info       # System information
eduos-exam       # Launch secure exam mode
eduos-admin      # Open administration console
eduos-learnhub   # Open learning portal (or http://localhost:5050)
eduos-devsuite   # Launch development environment
eduos-cyberlab   # Open cybersecurity labs
eduos-juiceshop  # Start OWASP Juice Shop (Docker)
burpsuite        # Launch Burp Suite Community Edition
eduos-hardening  # Apply system hardening
```

## 📋 System Users

| User | Password | Role |
|------|----------|------|
| `student` | *(random, written to `/etc/eduos/credentials.conf`)* | Daily learning |
| `exam` | *(random, written to `/etc/eduos/credentials.conf`)* | Restricted examinations |
| `admin` | *(set during installation)* | Lab administration |

## 🏗️ Architecture

| Module | Tech | Purpose |
|--------|------|---------|
| **Learn Hub** | Flask + SQLite | Study materials, assignments, schedule |
| **Exam Mode** | PyQt6 + Cryptography | Secure exams with encryption |
| **Admin Center** | PyQt6 | System monitoring and lab management |
| **Dev Suite** | PyQt6 | 12-tool development environment |
| **Cyber Lab** | PyQt6 + Docker | Isolated security practice labs |
| **Agent Service** | Python + MQTT/WebSocket | Background device monitoring daemon |
| **Central Server** | FastAPI + WebSocket | JWT-protected device broker |

## 🔒 Security

- UFW firewall, locked root, hardened SSH
- Restricted exam session: network/screenshot/terminal blocking
- Fernet-encrypted exam submissions with PBKDF2 key derivation
- Fernet-encrypted admin config with login gate
- JWT-authenticated agent↔server communication
- Process accounting and audit trails
- CyberLab containers isolated from host network

## 📁 Project Structure

```
~/EduOS/
├── AdminCenter/       # Administration console
├── Branding/          # Logo, wallpaper, themes
├── CyberLab/          # Security lab manager
├── DevSuite/          # Dev environment launcher
├── Documentation/     # Whitepaper and guides
├── ExamMode/          # Exam app + admin tool
├── LearnHub/          # Flask learning portal
├── Packages/          # Live-build ISO recipes
├── Scripts/           # Launchers and tools
├── Server/            # Central broker (FastAPI)
├── Services/          # Background agent daemon
├── tests/             # Pytest suite (agent + server)
├── .github/           # CI + ISO build workflows
├── CHANGELOG.md       # Complete build history
├── EDUOS_WHITEPAPER.md # Full system documentation
├── LICENSE            # Dual license (BSD open + proprietary)
└── README.md          # This file
```

## 🖥️ Pre-installed Development Tools



C, C++, Python, Java 21, JavaScript/Node.js, C# (.NET 8), Ruby, PHP, Perl — plus VS Code, Docker, Git, PostgreSQL, SQLite, CMake, and more.

## 🛡️ Pre-installed Security Tools

Wireshark, Nmap, Burp Suite, OWASP Juice Shop, SQLmap, John the Ripper, Hydra, Aircrack-ng, nikto, tcpdump, and more — all running in isolated environments.

## ⚙️ Available Scripts (Scripts/)

| Script | Purpose |
|--------|---------|
| `install-eduos.sh` | Full EduOS installation |
| `create-backup.sh` | Create system backup |
| `create-system-image.sh` | Build disk image for deployment |
| `eduos-desktop-setup.sh` | Apply KDE Plasma desktop layout |
| `eduos-admin-launcher.sh` | Launch Admin Center |
| `eduos-cyberlab-launcher.sh` | Launch Cyber Lab |
| `eduos-devsuite-launcher.sh` | Launch Dev Suite |
| `eduos-exam-launcher.sh` | Launch Exam Mode |
| `eduos-learnhub-launcher.sh` | Launch Learn Hub |
| `eduos-welcome.py` | First-run welcome wizard |
| `eduos-hardening.sh` | Apply system hardening |
| `install-docker.sh` | Docker setup script |

## 📜 License

EduOS uses a **dual-license structure**: open components under the BSD
2-Clause license, and proprietary components (ExamMode, AdminCenter,
Server, Services, InstitutionManager, CyberLab, LearnHub, DevSuite,
EcosystemDashboard) with all rights reserved.

See [LICENSE](LICENSE) for details. Contributions are welcome — see
[CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

*Built with ❤️ on FreeBSD 14.x · KDE Plasma 6*
