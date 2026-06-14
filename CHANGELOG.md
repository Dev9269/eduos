# EduOS Changelog

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
