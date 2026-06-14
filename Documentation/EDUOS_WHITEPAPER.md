# EduOS — Educational Operating System

## A Comprehensive Campus Computing Platform for Engineering Institutions

**Author:** Jainam  
**Version:** 1.0.0  
**Date:** June 14, 2026  
**Status:** Production Prototype  

---

## Executive Summary

EduOS is a Debian-based educational operating system designed specifically for engineering colleges and universities. It transforms a standard Debian Linux distribution into a unified campus computing platform that integrates learning resources, secure examinations, software development environments, cybersecurity laboratories, and centralized administration into a single, cohesive ecosystem.

Built on the stability of Debian 13 (Trixie) with the modern KDE Plasma 6 desktop environment, EduOS provides a Windows-like user experience that minimizes the learning curve for students and faculty while preserving the power and flexibility of Linux for advanced users.

This document provides a comprehensive overview of the EduOS architecture, modules, implementation details, security model, and deployment considerations.

---

## 1. Introduction and Vision

### 1.1 Problem Statement

Engineering institutions face several challenges in their computing environments:

- **Fragmentation**: Students and faculty rely on multiple unrelated software packages, web platforms, and operating systems.
- **Examination Security**: Conducting secure online examinations requires complex third-party software that is often expensive and unreliable.
- **Development Environment Setup**: Programming courses waste significant time on environment configuration rather than actual learning.
- **Cybersecurity Education**: Hands-on security practice requires isolated environments that are difficult to set up safely.
- **Lab Management**: IT administrators lack centralized tools for managing campus computer laboratories.
- **Cost**: Commercial educational software licenses are expensive for cash-strapped institutions.

### 1.2 Solution: EduOS

EduOS addresses these challenges by providing:

1. A **unified platform** that integrates all campus computing needs
2. A **built-in secure examination environment** that requires no third-party software
3. A **pre-configured development suite** ready for all engineering disciplines
4. **Isolated cybersecurity laboratories** for safe hands-on practice
5. **Centralized administration** tools for lab management and monitoring
6. An **affordable, open-source foundation** that eliminates licensing costs

### 1.3 Design Philosophy

- **Education-First**: Every feature is designed to serve an educational purpose.
- **Security by Default**: Secure configurations are the default, not an afterthought.
- **Familiar Experience**: Windows-like interface reduces training requirements.
- **Offline Capable**: Core features work without internet connectivity.
- **Reproducible Builds**: The entire system can be rebuilt from configuration files.
- **Incremental Deployment**: Institutions can adopt modules gradually.

---

## 2. System Architecture

### 2.1 Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 EduOS Applications                       │
│  ┌──────────┬──────────┬──────────┬──────────┬────────┐ │
│  │Learn Hub │Exam Mode │Admin     │Dev Suite │Cyber   │ │
│  │(Flask)   │(PyQt6)   │Center    │(PyQt6)   │Lab     │ │
│  │          │          │(PyQt6)   │          │(PyQt6) │ │
│  └──────────┴──────────┴──────────┴──────────┴────────┘ │
├─────────────────────────────────────────────────────────┤
│              EduOS System Configuration                  │
│  ┌──────────┬──────────┬──────────┬──────────┬────────┐ │
│  │Branding  │Desktop   │Users     │Security  │Services│ │
│  │Themes    │Profile   │& Roles   │Policies  │& Auto- │ │
│  │& Splash  │(KDE)     │          │(UFW,     │start   │ │
│  │          │          │          │iptables) │        │ │
│  └──────────┴──────────┴──────────┴──────────┴────────┘ │
├─────────────────────────────────────────────────────────┤
│              Debian 13 Base System                        │
│  ┌──────────┬──────────┬──────────┬──────────┬────────┐ │
│  │KDE       │Package   │Network   │Storage   │Virtual-│ │
│  │Plasma 6  │Manager   │Manager   │& Files   │ization │ │
│  │Desktop   │(APT)     │(NM)      │          │(KVM/   │ │
│  │          │          │          │          │Docker) │ │
│  └──────────┴──────────┴──────────┴──────────┴────────┘ │
├─────────────────────────────────────────────────────────┤
│              Linux Kernel 6.12 + Hardware                 │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Module Architecture

Each EduOS module is designed as an independent application that communicates through well-defined interfaces:

| Module | Technology | Purpose | Dependencies |
|--------|-----------|---------|-------------|
| Learn Hub | Flask + SQLite | Learning portal | Python, Flask |
| Exam Mode | PyQt6 + Cryptography | Secure exams | Python, PyQt6, cryptography |
| Admin Center | PyQt6 | System management | Python, PyQt6 |
| Dev Suite | PyQt6 | Dev environment | Python, PyQt6 |
| Cyber Lab | PyQt6 + Docker | Security labs | Python, PyQt6, Docker |

### 2.3 Technology Stack

| Component | Technology |
|-----------|-----------|
| Base OS | Debian 13 (Trixie) |
| Desktop | KDE Plasma 6.3.4 |
| Display Server | X11 (Plasma X11 session) |
| Window Manager | KWin |
| Display Manager | SDDM |
| Boot Splash | Plymouth |
| GUI Framework | PyQt6, Flask |
| Cryptography | Fernet (symmetric), PBKDF2 (key derivation) |
| Container Runtime | Docker CE |
| Virtualization | KVM/QEMU, libvirt |
| Database | SQLite (local), PostgreSQL (optional) |
| Packaging | APT, DEB |

---

## 3. Core Modules

### 3.1 Edu Learn Hub

**Purpose**: Centralized learning portal for students and educators.

**Features**:
- Study materials repository with subject-wise organization
- Assignment management with submission tracking
- Class and examination schedule
- Personal notes system
- Institutional announcements
- Timetable viewer
- Offline-first architecture (local SQLite database)
- Auto-starts via systemd user service on port 5050

**Architecture**:
```
learnhub_app.py
├── Flask web framework
├── SQLite database (learnhub.db)
│   ├── materials table
│   ├── assignments table
│   ├── notes table
│   ├── announcements table
│   └── schedule table
├── HTML/CSS templates (inline)
└── RESTful endpoints:
    ├── GET /          → Dashboard
    ├── GET /materials  → Study materials
    ├── GET /assignments → Assignments
    ├── GET /schedule   → Schedule
    ├── GET /notes      → Notes
    ├── GET /announcements → Announcements
    └── GET /timetable  → Timetable
```

**Pre-seeded Data**: 3 materials, 3 assignments, 3 announcements, 3 schedule entries.

### 3.2 Edu Exam Mode

**Purpose**: Secure digital examination environment.

**Features**:
- Security key authentication dialog
- Question types: MCQ, Multiple Select, Programming, Short Answer, Practical
- Configurable timer with visual countdown
- Auto-save every 30 seconds
- Auto-submit on timer expiration
- Encrypted local storage (Fernet symmetric encryption with PBKDF2 key derivation)
- PDF result generation via ReportLab (with plain text fallback)
- Full-screen kiosk mode (frameless, no decorations, stays on top)
- Key event restrictions (Print Screen, Alt+Tab, Super, Escape)
- Network isolation during examination (iptables rules)
- Virtual terminal blocking (tty1-4)
- Admin exam management tool

**Architecture**:
```
exam_app.py                     # Main exam application (student)
├── SecurityKeyDialog           # Authentication dialog
├── ExamTimer                   # Timer widget with progress bar
├── QuestionWidget              # Question rendering (5 types)
├── ExamWindow                  # Main full-screen window
│   ├── Key restrictions
│   ├── Auto-save mechanism
│   ├── Encrypted save (Fernet)
│   └── PDF generation (ReportLab)
└── load_exam_config()          # Config loader (JSON/encrypted)

exam_admin.py                   # Administration tool
├── ResultsTab                  # View and export results
├── CreateTab                   # Generate exam configurations
└── ControlTab                  # Session management

eduos-exam-session              # Restricted KDE session script
├── iptables network isolation
├── Screenshot key blocking (xmodmap)
├── Virtual terminal blocking (chmod 000)
├── KWin compositor disable
└── Automatic cleanup on exit

eduos-exam-shell                # Restricted shell for exam user
└── Only launches exam session
```

**Exam Configuration Format** (JSON):
```json
{
  "title": "Mid-Term Examination",
  "subject": "Computer Science",
  "duration_minutes": 60,
  "encryption_key": "sha256-hashed",
  "instructions": "Read carefully.",
  "questions": [
    {
      "type": "mcq",
      "question": "Question text",
      "options": ["A", "B", "C", "D"],
      "correct": "A"
    },
    {
      "type": "programming",
      "question": "Write code...",
      "language": "Python",
      "starter_code": "def solve():"
    }
  ]
}
```

**Security Model**:
```
Exam Start
    │
    ▼
Security Key Authentication
    │ (SHA-256 hash verification)
    ▼
System Restrictions Applied
    ├── iptables: Block all network (except localhost)
    ├── xmodmap: Disable Print Screen
    ├── chmod 000: Block tty1-4
    └── KWin: Disable compositing
    │
    ▼
Exam Application Runs (Fullscreen)
    ├── Frameless, no decorations
    ├── Window stays on top
    ├── Alt+Tab, Super, Escape blocked
    └── Auto-save every 30 seconds
    │
    ├── Timer Expires → Auto-submit
    └── Student Submits → Confirmation dialog
    │
    ▼
Encrypted Storage
    ├── Salt (16 bytes) + Fernet key (PBKDF2)
    ├── Encrypted JSON saved to ~/.eduos/exam/results/
    └── PDF report generated as secondary output
    │
    ▼
Cleanup
    ├── iptables rules flushed
    ├── tty permissions restored
    └── Session logs out
```

### 3.3 Edu Admin Center

**Purpose**: Centralized campus and laboratory management.

**Features**:
- Real-time system monitoring dashboard
- Lab machine inventory and status tracking
- Software management (install, remove, update)
- Examination session orchestration (start, stop, pause)
- Broadcast announcements to lab machines
- Report generation and export
- Resource usage monitoring (CPU, memory, disk, network)

**Architecture**:
```
eduos_admin.py
├── Dashboard
│   ├── System online count
│   ├── Active users
│   ├── Exams running
│   ├── Pending updates
│   └── Lab availability
├── Lab Systems Tab
│   ├── System list with IP, status, uptime
│   ├── Lock/unlock controls
│   └── Send message
├── Software Management Tab
│   ├── Installed packages list
│   ├── Install/remove/update controls
│   └── Pre-configured tool list
├── Exam Control Tab
│   ├── Session management
│   ├── Time remaining display
│   └── Start/stop/pause controls
└── Reports Tab
    ├── Usage reports
    ├── Exam summaries
    ├── Lab utilization
    └── Security audit logs
```

### 3.4 Edu Dev Suite

**Purpose**: Complete engineering programming environment.

**Pre-installed Tools**:

| Tool | Version/Package | Purpose |
|------|----------------|---------|
| VS Code | Latest | Primary IDE |
| GCC/G++ | 14 | C/C++ compilation |
| Python 3 | 3.13 | Python development |
| OpenJDK | 21 | Java development |
| Node.js | Latest | JavaScript/TypeScript |
| .NET SDK | 8.0 | C# development |
| Docker CE | 29 | Containerization |
| Git | Latest | Version control |
| CMake | Latest | Build system |
| PostgreSQL | 17 | Relational database |
| SQLite | 3.x | Embedded database |
| Kate | Latest | Advanced text editor |
| Geany | Latest | Lightweight IDE |
| Maven | Latest | Java build tool |
| Gradle | Latest | Build automation |
| Ruby | 3.x | Ruby development |
| PHP | 8.4 | Web development |
| Composer | Latest | PHP dependency manager |

**Architecture**:
```
devsuite_launcher.py
├── 12-tool grid interface
├── One-click launch for each tool
├── Tool version display
└── Professional icon-based UI
```

### 3.5 Edu Cyber Lab

**Purpose**: Isolated cybersecurity practice environment.

**Pre-configured Labs**:

| Lab | Tools | Difficulty | Container |
|-----|-------|-----------|-----------|
| Network Scanning | Nmap, netcat, tcpdump | Beginner | Kali Linux |
| Web Application Security | Burp Suite, SQLmap, Nmap | Intermediate | OWASP Juice Shop |
| Packet Analysis | tcpdump, Wireshark, tshark | Beginner | Kali Linux |
| Password Security | John, Hydra | Intermediate | Kali Linux |
| Digital Forensics | foremost, binwalk, strings | Advanced | Kali Linux |

**Installed Security Tools**:
- Wireshark (packet analysis)
- Nmap (network scanning)
- tcpdump (packet capture)
- netcat-openbsd (networking)
- Hydra (password attacks)
- John the Ripper (password cracking)
- SQLmap (SQL injection)
- Gobuster/Dirb (directory enumeration)
- Aircrack-ng (wireless security)
- Ettercap (MITM attacks)
- Macchanger (MAC address)
- ProxyChains (proxy routing)
- hping3 (network testing)
- slowhttptest (DoS testing)
- nikto (web server scanner)
- Shodan/Censys (network intelligence APIs)

**Safety Features**:
- All labs run in isolated Docker containers
- Default network mode: `--network=none` for offline labs
- Container cleanup on application exit
- Built-in warnings about legal and ethical use
- No attack tools exposed to host network by default

**Architecture**:
```
cyberlab.py
├── 5 pre-configured lab profiles
├── Docker container management
├── Built-in command console
├── Lab information display
└── Container lifecycle management
```

---

## 4. System Configuration

### 4.1 Desktop Environment

EduOS uses KDE Plasma 6 configured to provide a Windows 11-like experience:

| Setting | Value |
|---------|-------|
| Panel Layout | Floating, centered |
| Taskbar Alignment | Center |
| Window Decorations | Breeze (buttons on right) |
| Color Scheme | BreezeDark |
| Icon Theme | Papirus-Dark |
| Font | Inter (system), Fira Code (monospace) |
| Desktop Icons | Disabled |
| Animation Speed | Reduced |
| Compositor | OpenGL |

### 4.2 User Accounts

| Username | UID | Groups | Shell | Purpose |
|----------|-----|--------|-------|---------|
| jainam | 1000 | sudo, docker, libvirt | bash | Administrator/Developer |
| student | 1001 | student | bash | Daily learning |
| exam | 1002 | exam | eduos-exam-shell | Restricted examinations |
| admin | 1003 | sudo | bash | Lab administration |

### 4.3 Security Configuration

- **Firewall**: UFW enabled, default deny incoming, allow outgoing
- **Allowed Ports**: 22 (SSH), 5050 (Learn Hub)
- **Root Access**: Password locked (disabled)
- **SSH**: Root login disabled
- **Home Directories**: Permissions 750
- **Default Umask**: 027
- **Guest Account**: Disabled
- **Process Accounting**: Enabled (acct service)
- **Exam Isolation**: iptables, xmodmap, tty blocking

### 4.4 Startup Services

| Service | Purpose | Enabled |
|---------|---------|---------|
| docker | Container runtime | Yes |
| libvirtd | Virtualization | Yes |
| ssh | Remote access | Yes |
| ufw | Firewall | Yes |
| eduos-learnhub | Learning portal (user service) | Yes |
| sddm | Display manager | Yes |
| NetworkManager | Network management | Yes |

---

## 5. Development and Deployment

### 5.1 Project Structure

```
~/EduOS/
├── AdminCenter/
│   └── eduos_admin.py          # Administration console
├── Branding/
│   ├── logo/
│   │   └── eduos-logo.svg      # Scalable logo
│   ├── wallpaper/
│   │   └── eduos-wallpaper.png # Desktop wallpaper
│   ├── sddm/                   # Login screen theme
│   └── plymouth/               # Boot splash theme
├── CyberLab/
│   └── cyberlab.py             # Security lab manager
├── DevSuite/
│   └── devsuite_launcher.py    # Dev environment launcher
├── Documentation/
│   └── EDUOS_WHITEPAPER.md     # This document
├── ExamMode/
│   ├── exam_app.py             # Student exam application
│   ├── exam_admin.py           # Admin exam management
│   ├── exams/                  # Exam configuration files
│   ├── results/                # Encrypted submissions
│   └── config/                 # Exam system config
├── LearnHub/
│   └── learnhub_app.py         # Learning portal (Flask)
├── Scripts/
│   ├── eduos-welcome.py        # First-run wizard
│   ├── create-backup.sh        # System backup
│   ├── eduos-exam-launcher.sh
│   ├── eduos-admin-launcher.sh
│   ├── eduos-learnhub-launcher.sh
│   ├── eduos-devsuite-launcher.sh
│   └── eduos-cyberlab-launcher.sh
├── CHANGELOG.md                # Complete modification history
└── README.md                   # Project readme
```

### 5.2 System Files Installed

```
/usr/local/bin/
├── eduos-exam              # Exam mode launcher
├── eduos-admin             # Admin center launcher
├── eduos-learnhub          # Learn hub launcher
├── eduos-devsuite          # Dev suite launcher
├── eduos-cyberlab          # Cyber lab launcher
├── eduos-juiceshop         # Juice Shop launcher
├── eduos-info              # System info
├── eduos-hardening         # Hardening script
├── eduos-exam-session      # Restricted exam session
├── eduos-exam-shell        # Exam user shell
└── burpsuite               # Burp Suite launcher

/usr/share/applications/
├── eduos-learnhub.desktop
├── eduos-exammode.desktop
├── eduos-admincenter.desktop
├── eduos-devsuite.desktop
├── eduos-cyberlab.desktop
├── eduos-juiceshop.desktop
├── eduos-control-center.desktop
└── eduos-burpsuite.desktop

/usr/share/sddm/themes/eduos/   # SDDM login theme
/usr/share/plymouth/themes/eduos/ # Plymouth boot theme
/etc/sddm.conf.d/               # SDDM configuration
/etc/eduos-release              # OS release info
/etc/motd                       # Message of the day
```

### 5.3 Deployment Considerations

**Minimum Requirements**:
- 2 GB RAM (4 GB recommended)
- 20 GB disk space
- 2 CPU cores
- Network connectivity (for updates and Learn Hub)
- VirtualBox/KVM for virtualization features

**Deployment Models**:
1. **Standalone**: Single machine for student use
2. **Lab Network**: Multiple machines managed via Admin Center
3. **University Campus**: Integrated with institutional infrastructure

**Backup Recommendations**:
- Take VM snapshots before major changes
- Use `~/EduOS/Scripts/create-backup.sh` for configuration backups
- Regularly export examination results

---

## 6. Roadmap

### Phase 1: Foundation ✅ (Complete)
- [x] System assessment and configuration
- [x] KDE Plasma Windows 11 customization
- [x] Development environment installation
- [x] Branding (logo, wallpaper, themes, splash)

### Phase 2: Core Modules ✅ (Complete)
- [x] Edu Exam Mode (application + restricted session)
- [x] Edu Admin Center (management console)
- [x] Edu Learn Hub (learning portal)
- [x] Edu Dev Suite (development environment)
- [x] Edu Cyber Lab (security labs)

### Phase 3: Production Hardening 🔄 (In Progress)
- [x] System hardening and firewall
- [x] Restricted exam session
- [x] Security configurations
- [ ] User acceptance testing
- [ ] Performance optimization

### Phase 4: Campus Integration 📋 (Planned)
- [ ] LDAP/SSO authentication
- [ ] Network file sharing (NFS)
- [ ] Centralized exam server
- [ ] LMS integration (Moodle API)
- [ ] Multi-lab orchestration
- [ ] Software RAID/backup solutions

### Phase 5: Distribution 📦 (Planned)
- [ ] Debian live-build ISO generation
- [ ] Automated installer
- [ ] PXE network boot support
- [ ] Docker-based EduOS image
- [ ] Cloud deployment templates

---

## 7. Conclusion

EduOS represents a complete rethinking of how educational computing environments should work. By integrating learning, examinations, development, cybersecurity, and administration into a single, cohesive platform built on Debian Linux, it eliminates the fragmentation, cost, and complexity that plague current campus computing solutions.

The system has been successfully built and deployed on a VirtualBox virtual machine running Debian 13 with KDE Plasma 6. All five core modules are functional and ready for testing. The project is designed for incremental adoption — institutions can start with basic desktop deployment and gradually enable advanced features as needed.

EduOS is a personal, private project. All source code, configurations, and documentation are maintained in the `~/EduOS/` directory on the reference VM.

---

*EduOS — Education First, Security Always.*
