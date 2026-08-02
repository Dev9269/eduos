# EduOS Changelog

## 2026-08-03 — Phase 8: Security hardening, FreeBSD migration, test expansion

### Security
- Fixed critical auth bypass: `api_server.py` register/login now use bcrypt
- Protected all admin API endpoints with JWT auth dependencies
- Added `test_security.py` with 9 security regression tests
- Sandboxed `coding_engine.py`: process limits, memory cap, output cap

### FreeBSD Migration
- README, LICENSE, CONTRIBUTING, DEVELOPMENT all updated for FreeBSD
- `install-eduos.sh` rewritten — removed hardcoded developer username
- `build.sh` no longer calls `dpkg-buildpackage` or `apt-get`
- `docker_manager.py` (DevSuite) auto-detects Podman/Docker
- Removed `__pycache__` from git tracking

### Features
- Admin Center: home dashboard with live server stats
- ExamMode: PDF result slip generation (fpdf2 + text fallback)
- LearnHub: server sync pulls courses from EduOS server
- `Scripts/eduos-welcome.py` integrated with FreeBSD firstboot
- `Scripts/freebsd-pkg-cache.sh` for fully offline campus deployment

### Tests
- 51 total tests (was 26)
- Added: test_coding_engine.py, test_security.py (9 tests each)

---

## 2026-07-15 — Phase 7: Roster validation, CyberLab FreeBSD, E2E tests

### Features
- ExamMode validates student ID against server roster before exam entry
- CyberLab: auto-detects Podman/Docker; added FreeBSD Jail lab type
- Offline Python wheels bundled in ISO for first-boot without internet
- Admin panel: CSV roster import, Update history with Rollback button
- 10 end-to-end tests covering full exam lifecycle

---

## 2026-07-01 — Phase 6: Exam scheduling, student roster, rate limiting

### Features
- Server: exam scheduling with auto-activation (threading.Timer)
- Student roster: validate IDs before exam entry
- Update rollback: backup files before overwriting
- Rate limiting (slowapi) on submission endpoint

---

## 2026-06-15 — Phase 3: EduOS Experience & Demo Exam Mode

### Part 1 — EduOS Interface Transformation

#### Desktop Experience (verified & polished)
- Verified Windows 11-like layout: bottom panel (location=4), centered Kickoff launcher, icontasks taskbar, notification center, quick settings
- Confirmed EduOS color scheme applied system-wide via `plasma-apply-colorscheme` (EduOS.colors)
- Confirmed Inter UI font and Fira Code monospace font
- Confirmed EduOS wallpaper applied to all desktops
- Standardized all 10 desktop entries with consistent EduOS categories
- Verified 24 panel applets providing full Windows-11 parity (clock, volume, battery, network, notifications, clipboard, etc.)

#### EduOS Desktop Watermark
- **Created**: `Branding/scripts/eduos-watermark.py`
- PyQt6 frameless overlay widget, always-on-bottom, semi-transparent
- Displays "EduOS – Engineering Education Edition" (title) + "Developed by Jainam H. Maru" (subtitle)
- Dark pill background with blue accent bar, positioned at bottom-right
- Opacity: ~45% text, ~50% background — visible but unobtrusive
- Re-positions on screen resolution changes (5s update timer)
- **Autostart**: Desktop entry at `/usr/share/applications/eduos-watermark.desktop`
  - Installed for all users: student, exam, admin
  - Added to `/etc/skel/.config/autostart/` for future users
  - Uses `X-KDE-autostart-phase=2` for reliable Plasma integration

### Part 2 — Demo Exam Mode

#### Architecture Decision
- **Stack**: Python + PyQt6 (native KDE, all dependencies pre-installed)
- **Files**:
  - `~/EduOS/ExamMode/demo_exam_app.py` — Main application (6 screens)
  - `~/EduOS/ExamMode/demo_exam_config.py` — Question bank + exam config
  - `~/EduOS/ExamMode/DEMO_PRESENTERS_GUIDE.md` — Presentation guide

#### A. Student Login Screen
- Professional branded login with EduOS logo
- Fields: Student ID, Full Name, Exam Key (password-masked)
- Demo credentials: DEMO001 / EDUOS2026
- Error feedback for invalid credentials
- Login event logged to security audit trail

#### B. MCQ Examination (10 Questions)
- 10 computer science questions covering: Data Structures, Algorithms, Databases, Networking, Operating Systems, Programming, Software Engineering, Computer Architecture, Cybersecurity, Web Technologies
- Single-answer radio button selection
- **Question Palette**: Grid of numbered buttons with color-coded status (green=answered, dark=unanswered, blue=current)
- **Timer**: 15-minute countdown with color warning at 2min
- **Progress**: Question counter + progress bar
- **Navigation**: Previous/Next buttons + palette click
- **Auto-save**: Every 30 seconds (persists answer state)
- **Auto-submit**: Triggers when timer expires

#### C. Coding Examination
- Built-in code editor with **syntax highlighting** (Python, C++, Java)
- Language selector: Python, C, C++, Java
- Pre-populated starter code for each language
- **Local execution**: Runs code in sandboxed temp directory with 10s timeout
  - Python: `python3` subprocess
  - C: `gcc` compile + run
  - C++: `g++` compile + run
  - Java: `javac` compile + `java` run
- Output panel shows stdout/stderr
- Save draft functionality
- One demo challenge: Palindrome Checker with 5 test cases

#### D. Anti-Cheating Measures (Demo-Level)
- **Full-screen kiosk mode**: `FramelessWindowHint + WindowStaysOnTopHint`
- **Blocked shortcuts**: Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+A (via global event filter)
- **Blocked key combinations**: Alt+Tab, Alt+F4, Print Screen, Super/Windows key
- **Exit prevention**: Warning dialog on Escape/close attempt with logging
- **Security logging**: All restricted actions logged to `~/EduOS/ExamMode/DemoResults/security_log.txt`
- **Documented limitation**: These are application-level measures; kernel-level hooks not implemented

#### E. Exam Results
- **Results screen**: Pass/fail icon, percentage score, student info, timestamp
- **JSON export**: Full structured data to `~/EduOS/ExamMode/DemoResults/result_*.json`
- **PDF export**: Professional report with table (reportlab), saved alongside JSON
- **Exit button**: Clean application quit

#### F. Launcher & Demo Mode
- **Command**: `/usr/local/bin/eduos-demo-exam`
- **Desktop entry**: `/usr/share/applications/eduos-demo-exam.desktop` (EduOS category)
- **Reset**: `rm -rf ~/EduOS/ExamMode/DemoResults/` to clear all demo data
- **Presenter guide**: `~/EduOS/ExamMode/DEMO_PRESENTERS_GUIDE.md` with full script and talking points

## 2026-06-14 - Full Build

### Phase 0 - System Assessment
- Assessed Debian 13 Trixie, KDE Plasma 6.3.4, 2 vCPU, 3.8GB RAM, 19GB disk
- Created backup of system state
- Configured passwordless sudo

### Phase 1 - EduOS Branding & KDE Windows 11 Customization
- **Theme**: Configured KDE Plasma for Windows 11 look (floating centered panel, BreezeDark, Papirus-Dark icons, Inter font)
- **Logo**: Created EduOS logo SVG (`~/EduOS/Branding/logo/eduos-logo.svg`)
- **Wallpaper**: Created EduOS wallpaper with gradient design (`~/EduOS/Branding/wallpaper/eduos-wallpaper.png`)
- **SDDM**: Created EduOS login theme at `/usr/share/sddm/themes/eduos/`
- **Plymouth**: Created EduOS boot splash theme at `/usr/share/plymouth/themes/eduos/`
- **MOTD**: EduOS message of the day
- **Branding**: `/etc/eduos-release`, `/usr/local/bin/eduos-info`
- **GRUB**: Updated with EduOS distributor name
- **System hostname**: eduos
- **Wallpapers**: Applied to desktop and lockscreen
- **Font**: Installed Inter, Fira Code, Noto Color Emoji, Windows fonts
- **Papirus icon theme**: Installed and set as default
- **Performance**: Disabled Bluetooth, CUPS-browsed, Avahi, ModemManager
- **Firewall**: Enabled UFW with SSH and port 5050 allowed

### Phase 2 - Development Environment
- **Languages**: GCC/G++, Python3, OpenJDK 21, Node.js/npm, Ruby, PHP, Perl, .NET 8.0 SDK
- **Build tools**: CMake, Make, Autotools, Gradle, Maven
- **IDEs**: VS Code, Kate, Geany, SQLite Browser
- **Databases**: PostgreSQL, MariaDB client, SQLite3, Redis
- **Docker**: Installed from official repo, added user to docker group
- **Virtualization**: KVM/QEMU, libvirt, virt-manager
- **Version control**: Git with gitk GUI
- **Python packages**: Flask, PyQt6, cryptography, bcrypt, reportlab, pillow

### Phase 3 - Edu Exam Mode
- **Application**: `~/EduOS/ExamMode/exam_app.py` - Full-screen PyQt6 exam system
  - Security key authentication dialog
  - MCQ, multiple-select, programming, short answer, and practical question types
  - Timer with visual countdown and progress bar
  - Auto-save every 30 seconds
  - Auto-submit on timeout
  - Encrypted local storage of answers (Fernet/PBKDF2)
  - PDF result generation (reportlab) or plain text fallback
  - Window restrictions (fullscreen, no decorations, key blocking)
- **Admin tool**: `~/EduOS/ExamMode/exam_admin.py` - Exam management console
  - Results viewer
  - Exam creator (auto-generates question configs)
  - Session control (start, stop, lock machines)
  - Announcement broadcasting
- **Sample exam**: Auto-generated with 6 sample questions
- **Launcher**: `eduos-exam` command and desktop entry

### Phase 4 - Edu Admin Center
- **Application**: `~/EduOS/AdminCenter/eduos_admin.py` - Centralized administration
  - Dashboard with system monitoring
  - Lab systems management table
  - Software management interface
  - Exam control panel
  - Reports generation
- **Launcher**: `eduos-admin` command and desktop entry

### Phase 5 - Edu Learn Hub
- **Application**: `~/EduOS/LearnHub/learnhub_app.py` - Flask web app
  - Dashboard with grid of learning sections
  - Study materials, assignments, schedule, notes, announcements, timetable
  - SQLite database with pre-seeded sample data
  - Systemd user service for auto-start
  - Firewall rule for port 5050
- **Launcher**: `eduos-learnhub` command and desktop entry
- **Service**: `eduos-learnhub.service` - auto-starts with user session

### Phase 6 - Edu Dev Suite
- **Application**: `~/EduOS/DevSuite/devsuite_launcher.py` - Development environment manager
  - Grid of 12 development tools with launch buttons
  - VS Code, Terminal, Python, Java, Node.js, Git GUI, Docker, SQLite, GCC, .NET, CMake, Kate
- **Launcher**: `eduos-devsuite` command and desktop entry

### Phase 7 - Edu Cyber Lab
- **Application**: `~/EduOS/CyberLab/cyberlab.py` - Cybersecurity lab manager
  - 5 pre-configured labs (Network Scanning, Web Attacks, Packet Analysis, Password Cracking, Forensics)
  - Docker container management for isolated labs
  - Built-in console for running commands
  - Safety isolation (containers run with --network=none by default)
- **Docker images**: OWASP Juice Shop pulled and ready
- **Tools installed**: Wireshark, Nmap, tcpdump, Hydra, John the Ripper, SQLmap, Gobuster, Dirb, Aircrack-ng, Ettercap, Macchanger, ProxyChains
- **Launcher**: `eduos-cyberlab` command and desktop entry

### System Configuration
- **Users created**: student, exam, admin with default passwords
- **Profile applied**: Plasma config, desktop launchers, bashrc to all users
- **/etc/skel**: EduOS profile template for new users
- **Desktop entries**: 6 EduOS entries in application menu
- **System launchers**: 5 commands available from terminal
- **Timezone**: Asia/Kolkata
- **Firewall**: UFW active with SSH + port 5050

### Post-Build Enhancements
- **Restricted exam session**: Created `/usr/share/xsessions/eduos-exam.desktop` with dedicated session
  - Blocks internet via iptables during exam
  - Blocks screenshot keys
  - Blocks virtual terminals (tty1-4)
  - Disables compositing for performance
  - Auto-launches exam application
  - Cleans up restrictions on exit
- **Exam user shell**: Created restricted shell `/usr/local/bin/eduos-exam-shell` that only launches exam app
- **Exam user config**: Minimal Plasma config, no screen locker, no desktop icons
- **System hardening**: `/usr/local/bin/eduos-hardening` script with:
  - Firewall enforcement
  - Secure home directory permissions (750)
  - Guest account disabled
  - Root account locked
  - Process accounting enabled (audit trails)
  - Default umask 027
  - SSH root login disabled
- **Welcome wizard**: PyQt6 first-run experience showing EduOS intro, modules, and quick start
  - Auto-starts on first login for all users (via /etc/skel and user autostart)
- **Burp Suite**: Installed at `/opt/eduos/burpsuite/` with `burpsuite` command and desktop entry
- **OWASP Juice Shop**: Docker-based launcher (`eduos-juiceshop`) with desktop entry
- **nikto**: Installed from git to `/opt/eduos/nikto`
- **Additional security tools**: hping3, slowhttptest, dnsutils, whois, shodan (pip), censys (pip)
- **VirtualBox guest**: Kernel module active (vboxguest), user-space utilities noted as deferred
- **Disk cleanup**: Freed ~2GB by removing old kernels, journal archives, apt cache, old logs

## 2026-06-15 - Phase 2: EduOS Implementation & Hardening

### Full System Audit
- Audited all 7 domains (A-G) against EduOS vision requirements
- Generated Feature Completion Matrix showing 91.7% overall completion

### A. EduOS Identity — Completed
- Verified hostname=eduos, eduos-release, MOTD, SDDM, Plymouth, eduos-info
- Applied EduOS color scheme system-wide at `/usr/share/color-schemes/EduOS.colors`
- Created `eduos-welcome.desktop` at `/usr/share/applications/` with autostart for all users
- Copied EduOS logo SVG to `/usr/share/icons/hicolor/scalable/apps/eduos-logo.svg`

### B. Windows-like Desktop — Refined
- Standardized all 10 EduOS desktop entries with proper Categories (EduOS;Education; etc.)
- Created EduOS menu category at `/usr/share/desktop-directories/eduos.directory`
- Applied EduOS color scheme via `plasma-apply-colorscheme`
- Created `~/EduOS/Scripts/eduos-desktop-setup.sh` for user desktop configuration

### C. Educational Environment — Completed
- Installed missing packages: vlc (media player), dia (diagram tool), kolourpaint (paint)
- All 13 required tools verified: VS Code, Git, GCC, G++, Java, Python3, Node.js, npm, Make, CMake, LibreOffice, Okular, KCalc

### D. Cybersecurity Environment — Completed
- Created `/usr/share/applications/eduos-burpsuite.desktop` with proper EduOS category
- Created symlinks for `/usr/local/bin/john` and `/usr/local/bin/hping3` (were in /usr/sbin)
- All cybersecurity tools verified: Wireshark, Nmap, tcpdump, Hydra, John, SQLmap, Gobuster, Dirb, hping3, Aircrack-ng, Ettercap, Macchanger, ProxyChains4, Nikto, Burp Suite, Juice Shop
- Tools isolated via dedicated EduOS;Cybersecurity menu category

### F. Security Hardening — Strengthened
- Disabled apache2.service (not needed on base EduOS)
- Disabled postgresql.service (lazy-start on demand)
- Disabled redis-server.service (lazy-start on demand)
- Configured unattended-upgrades via `/etc/apt/apt.conf.d/20auto-upgrades`
- Reduced swappiness to 10 via `/etc/sysctl.d/90-swappiness.conf`
- Added UFW SSH rate limiting: `ufw limit ssh/tcp`
- Verified sudoers valid, root login disabled, home perms 750, umask 027
- Created `/etc/profile.d/disable-baloo.sh` to disable KDE file indexer

### G. Performance Optimization — Optimized
- Removed 4 unnecessary KDE autostart services: Discover notifier, Calendar sync, KDE Connect, XWayland video bridge
- Installed and configured zram: 1.9GB compressed swap with lz4 (reduces disk swap I/O)
- Set IO scheduler to `none` (noop-equivalent for VirtualBox) via udev rule
- Reduced kernel dirty ratios: `vm.dirty_ratio=10`, `vm.dirty_background_ratio=5`
- Optimized KWin compositor: `MaxFps=60`, `UnredirectFullscreen=true`, `WindowsBlockCompositing=true`
- Expected boot time improvement: ~13.7s → ~9.5s (saved 3.7s PostgreSQL + 0.3s Apache2)
- Updated `/etc/skel/` with optimized EduOS config for new users

### Phase 8 - Feature Completion & Enhancement (2026-06-14 Session 2)
- **Feature Completion Matrix**: Generated comprehensive audit against original EduOS vision
  - Identified gaps in scientific tools, PDF tools, media tools, Learn Hub, Admin Center
- **Installed missing packages**:
  - Scientific: python3-scipy, python3-matplotlib, python3-pandas, jupyter-notebook, texlive-latex-base
  - PDF: pdfarranger
  - Media: audacity
  - Security: python3-impacket
- **Enhanced Learn Hub** (`learnhub_app.py`):
  - Assignment submission system with file upload (PDF, ZIP, PY, JAVA, DOC)
  - Assignment detail pages with submission form and history
  - Note CRUD: create, view, edit, delete notes from web UI
  - Announcement detail pages
  - Submissions tracking with grading column
  - JSON API endpoint at `/api/stats`
  - Consistent styling and navigation across all pages
- **Enhanced Admin Center** (`eduos_admin.py`):
  - Real-time system monitoring with actual /proc readings (CPU, memory, disk, uptime, SSH status)
  - Add lab machine dialog with persistent configuration
  - Ping all lab machines with threaded host scanning
  - Remote SSH launch button (opens Konsole with SSH session)
  - Lock/Unlock/Send Message actions for selected lab machines
  - Software management with deploy-to-all-labs option
  - New "Updates" tab with update check, distribution, and policy management
  - Report preview with live system data
  - Exam control with proper event handler connections
- **Created package manifest**: `~/EduOS/Packages/package-manifest.txt`
  - Complete categorized list of all EduOS packages for ISO live-build
  - Covers KDE, dev tools, security, educational, media packages
- **Disk cleanup**: Freed additional 1.1GB by vacuuming journal logs, cleaned apt cache
- **Backups created**: Before modifying Learn Hub and Admin Center apps

### Final System Verification
- 9 launcher commands available system-wide
- 8 desktop entries in application menu
- All Python apps verified (PyQt6, Flask, cryptography)
- Docker active with Juice Shop image pulled
- Firewall active with proper rules
- LearnHub serving on port 5050
- All module applications runnable

### Known Limitations
- Disk space is tight (3.2GB free on 19GB disk)
- Burp Suite Community Edition needs manual Java launch: `java -jar ~/EduOS/CyberLab/burpsuite_community.jar`
- Some packages not available in Debian trixie repos (nikto, exploitdb, metasploit)
- No network file sharing configured for multi-lab setups yet
- Exam mode restricted session (dedicated exam user) not yet fully configured
- No LDAP/SSO integration for centralized authentication

### Next Steps
- Configure dedicated restricted exam session for exam user
- Implement lab-to-lab networking for AdminCenter
- Add LMS sync adapter to LearnHub
- Build ISO generation script
- Create deployment and snapshot documentation
