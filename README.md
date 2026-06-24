<div align="center">

# 📚 EduOS

[![Stars](https://img.shields.io/github/stars/Dev9269/eduos?style=flat-square&logo=github&color=gold)](https://github.com/Dev9269/eduos)
[![Forks](https://img.shields.io/github/forks/Dev9269/eduos?style=flat-square&logo=github&color=blue)](https://github.com/Dev9269/eduos/forks)
[![License](https://img.shields.io/github/license/Dev9269/eduos?style=flat-square&color=brightgreen)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=flat-square)](https://github.com/Dev9269/eduos/pulls)

Debian-based educational OS for engineering colleges — integrating learning, secure exams, dev tools, cyber labs, and campus administration.

**Created by** [Jainam Maru](https://github.com/Dev9269)

</div>

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
| `jainam` | *(personal)* | Administrator / Developer |
| `student` | `student123` | Daily learning |
| `exam` | `exam123` | Restricted examinations |
| `admin` | `admin123` | Lab administration |

## 🏗️ Architecture

| Module | Tech | Purpose |
|--------|------|---------|
| **Learn Hub** | Flask + SQLite | Study materials, assignments, schedule |
| **Exam Mode** | PyQt6 + Cryptography | Secure exams with encryption |
| **Admin Center** | PyQt6 | System monitoring and lab management |
| **Dev Suite** | PyQt6 | 12-tool development environment |
| **Cyber Lab** | PyQt6 + Docker | Isolated security practice labs |

## 🔒 Security

- UFW firewall, locked root, hardened SSH
- Restricted exam session: network/screenshot/terminal blocking
- Fernet-encrypted exam submissions with PBKDF2 key derivation
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
├── Scripts/           # Launchers and tools
├── CHANGELOG.md       # Complete build history
├── EDUOS_WHITEPAPER.md # Full system documentation
├── LICENSE            # MIT License
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

MIT License — Copyright (c) 2026 Jainam

This is a personal, private project. Use freely for educational purposes.

---

*Built with ❤️ on Debian 13 Trixie · KDE Plasma 6*
