# EduOS v3.0 User Guide

> Version 3.0 | July 2026

---

## Table of Contents

1. [Welcome to EduOS](#welcome-to-eduos)
2. [First Boot](#first-boot)
3. [Desktop Navigation](#desktop-navigation)
4. [Application Overview](#application-overview)
5. [File Management](#file-management)
6. [Network Configuration](#network-configuration)
7. [Printing](#printing)
8. [Accessibility](#accessibility)
9. [Getting Help](#getting-help)

---

## Welcome to EduOS

EduOS is a complete educational operating system designed for students and faculty. It provides all the tools needed for learning, teaching, and collaboration in a secure, privacy-respecting environment.

### Key Applications

| Application | Purpose |
|-------------|---------|
| **Learn Hub** | Access course materials, assignments, and AI tutoring |
| **Exam Portal** | Take secure online exams |
| **Cyber Lab** | Practice cybersecurity skills in a safe environment |
| **Dev Suite** | Write and compile code in multiple languages |
| **Admin Center** | Manage your account and settings (for faculty) |

---

## First Boot

### 1. Starting EduOS

1. Power on your computer with the EduOS USB drive inserted
2. You will see the **GRUB boot menu** with the EduOS branding
3. Select **"EduOS v3.0"** and press Enter
4. The system will boot showing the EduOS splash screen

### 2. Login Screen (SDDM)

- **For pre-enrolled devices**: Your username and password are provided by your institution's IT department
- **For standalone/live session**: Login with `edos` / `edos`

### 3. First-Time Setup Wizard

On first boot, the EduOS Setup Assistant will guide you through:

1. **Language Selection** — Choose your preferred language
2. **Keyboard Layout** — Select your keyboard layout
3. **Timezone** — Set your timezone
4. **Network** — Connect to Wi-Fi or Ethernet
5. **Account Setup** — Create or link your educational account
6. **Privacy Settings** — Configure telemetry and data sharing preferences
7. **Tour** — Optional guided tour of the desktop

> **Note**: Settings can be changed later from System Settings.

### 4. Desktop Overview

```
┌──────────────────────────────────────────────────────────────┐
│  Panel (Top): [App Menu] [Clock] [System Tray] [Notification]│
├──────────────────────────────────────────────────────────────┤
│                                                              │
│     ┌───┐  ┌───┐  ┌───┐  ┌───┐  ┌───┐  ┌───┐              │
│     │LH │  │EP │  │CL │  │DS │  │AC │  │UM │              │
│     └───┘  └───┘  └───┘  └───┘  └───┘  └───┘              │
│     Learn  Exam   Cyber  Dev   Admin  Update               │
│     Hub    Portal  Lab    Suite  Center Manager             │
│                                                              │
│                                                              │
│                    Desktop Widgets                           │
│                    ┌────────────────┐                       │
│                    │  Today's       │                       │
│                    │  Schedule      │                       │
│                    │  ─────────     │                       │
│                    │  09:00 Math    │                       │
│                    │  11:00 Physics │                       │
│                    │  14:00 Lab     │                       │
│                    └────────────────┘                       │
│                                                              │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  Panel (Bottom): [Workspace] [Task Manager] [Virtual Kbd]   │
└──────────────────────────────────────────────────────────────┘
```

---

## Desktop Navigation

### Desktop Environment

EduOS uses **KDE Plasma 6** with a custom EduOS theme.

### Key Navigation Elements

| Element | Location | Description |
|---------|----------|-------------|
| **Application Menu** | Top-left | Access all installed applications |
| **Top Panel** | Screen top | Clock, system tray, notifications |
| **Bottom Panel** | Screen bottom | Task manager, virtual desktop switcher |
| **Desktop** | Main area | Widgets, shortcuts, folder view |
| **System Tray** | Top-right | Network, volume, battery, updates |

### Common Actions

- **Search for applications**: Press `Alt + F2` or click the Application Menu and start typing
- **Switch between windows**: Press `Alt + Tab`
- **Switch virtual desktops**: Press `Ctrl + F1` through `Ctrl + F4`
- **Take screenshot**: Press `Print Screen`
- **Lock screen**: Press `Meta + L` (Windows key + L)
- **Open terminal**: Press `Ctrl + Alt + T`
- **Show desktop**: Press `Meta + D`

### Customizing the Desktop

1. Right-click on the desktop and select **Configure Desktop**
2. Choose wallpaper, widgets, and layout options
3. To add widgets: Right-click desktop → **Add Widgets**
4. Panel settings: Right-click panel → **Edit Panel**

---

## Application Overview

### Learn Hub

Learn Hub is your central portal for all academic content.

```
Learn Hub
├── Dashboard
│   ├── Upcoming assignments
│   ├── Recent grades
│   └── Course announcements
├── Courses
│   ├── [Course Name]
│   │   ├── Syllabus
│   │   ├── Materials (documents, videos, links)
│   │   ├── Assignments
│   │   ├── Quizzes
│   │   └── Grades
│   └── [Course Name]...
├── AI Tutor
│   ├── Chat interface
│   ├── Subject-specific help
│   └── Practice problems
└── Calendar
    ├── Class schedule
    ├── Exam dates
    └── Office hours
```

**Launch**: Click the Learn Hub icon on the desktop or find it in the Application Menu.

### Exam Portal

The Exam Portal is your interface for taking secure online exams.

> **Important**: During an exam, EduOS enters **Lockdown Mode**. This restricts:
> - Access to other applications
> - Internet browsing (except the exam server)
> - Copy/paste functionality
> - USB mass storage devices

**To take an exam**:
1. Open Exam Portal from the desktop
2. Authenticate with your credentials (and MFA if enabled)
3. Select the active exam from your list
4. Read the instructions carefully
5. Click **Start Exam** (timer begins)
6. Answer questions using the provided interface
7. Review your answers
8. Click **Submit** when finished

**Exam question types**:
- **Multiple Choice** — Select one or more correct answers
- **Coding** — Write and test code in an online editor
- **Essay** — Type or upload written responses
- **File Upload** — Submit PDF, images, or other files
- **Interactive** — Drag-and-drop, ordering, matching exercises

### Cyber Lab

A safe, isolated environment for learning cybersecurity.

```
Cyber Lab
├── Scenarios
│   ├── Beginner
│   │   ├── Password cracking basics
│   │   ├── Network scanning
│   │   └── Social engineering awareness
│   ├── Intermediate
│   │   ├── SQL injection
│   │   ├── XSS attacks
│   │   └── Privilege escalation
│   └── Advanced
│       ├── CTF competitions
│       ├── Malware analysis
│       └── Penetration testing
├── Tools
│   ├── Nmap, Wireshark, Metasploit
│   ├── Burp Suite, John the Ripper
│   └── Custom lab environments (Docker)
└── Progress
    ├── Completed scenarios
    ├── Certificates earned
    └── Skill points
```

### Dev Suite

A complete development environment with support for multiple programming languages.

| Language | Compiler/Interpreter | Editor/IDE |
|----------|---------------------|------------|
| Python 3 | Python 3.12 | PyCharm, VS Code |
| C/C++ | GCC 13, Clang 16 | VS Code, Qt Creator |
| Java | OpenJDK 17 | IntelliJ IDEA, VS Code |
| JavaScript/TypeScript | Node.js 20, Deno | VS Code, WebStorm |
| Rust | rustc 1.75 | VS Code, RustRover |
| Go | Go 1.22 | VS Code, GoLand |
| HTML/CSS | — | VS Code, Bluefish |
| SQL | PostgreSQL 16 | pgAdmin, DBeaver |
| Bash | Bash 5.2 | VS Code, Vim |

### Admin Center

Available for faculty and administrators. See the Administrator Guide for details.

### Update Manager

Keeps your system up-to-date.

| Feature | Description |
|---------|-------------|
| **Automatic Updates** | Security patches installed automatically |
| **Manual Updates** | Click to check and install available updates |
| **Update Schedule** | Configure maintenance windows |
| **Release Notes** | View changes in each update |
| **Rollback** | Revert to a previous system state if needed |

---

## File Management

### Dolphin File Manager

EduOS uses **Dolphin** as the default file manager.

**Opening Dolphin**:
- Click the folder icon in the bottom panel
- Press `Meta + E`
- From Application Menu → Utilities → Dolphin

### Key Features

| Feature | How To |
|---------|--------|
| Browse files | Click folders in the main view |
| Search | Press `Ctrl + F` or type in search bar |
| Create folder | `Ctrl + Shift + N` |
| Copy | `Ctrl + C`, then `Ctrl + V` |
| Move | `Ctrl + X`, then `Ctrl + V` |
| Delete | `Delete` key (moves to Trash) |
| Permanent delete | `Shift + Delete` |
| Rename | `F2` |
| View options | `Ctrl + 1` (Icons), `Ctrl + 2` (Details) |
| Split view | `F3` |
| Terminal | `F4` (embedded terminal) |
| Properties | `Alt + Enter` |
| Bookmarks | Drag folder to Places panel |
| Tabs | `Ctrl + T` |

### Common Locations

| Location | Path | Description |
|----------|------|-------------|
| Home | `/home/edos/` | Your personal files |
| Documents | `~/Documents/` | Course documents |
| Downloads | `~/Downloads/` | Downloaded files |
| Assignments | `~/Documents/Assignments/` | Coursework submissions |
| Projects | `~/Projects/` | Coding projects |
| Shared | `/srv/shared/` | Institution-shared files |
| USB Drive | `/media/edos/` | External storage (auto-mounts) |

### External Drives

1. Connect a USB drive or external hard disk
2. A notification will appear — click to open
3. The drive appears in Dolphin under **Devices**
4. To safely remove: right-click the drive → **Safely Remove**

---

## Network Configuration

### Connecting to Wi-Fi

1. Click the **Network icon** in the system tray (top-right)
2. Click your Wi-Fi network name
3. Enter the password and click **Connect**
4. The icon changes to indicate connected status

### Wired (Ethernet) Connection

- Plug in an Ethernet cable — connection is automatic
- Status is shown in the network applet

### EduOS Network Profiles

EduOS supports network profiles for different environments:

| Profile | Use Case | Features |
|---------|----------|----------|
| **Campus** | On-campus network | Full access, authentication via 802.1X |
| **Home** | Home network | Standard connectivity |
| **Exam** | During exams | Restricted to exam server only |
| **Library** | Public WiFi | Filtered, proxy-configured |
| **VPN** | Remote access | WireGuard VPN to institution |

**To switch profiles**:
1. Right-click the Network icon
2. Select **Network Profiles**
3. Choose the desired profile

### Proxy Configuration

If your institution requires a proxy:

1. Open System Settings → Network → Proxy
2. Enter your proxy details
3. Apply the settings

---

## Printing

### Adding a Printer

1. Open System Settings → Printers
2. Click **Add Printer**
3. Select your printer:
   - **Network Printer** — Detected automatically on the local network
   - **USB Printer** — Connect and it should appear
   - **IPP/CUPS** — Enter the printer address manually
4. Follow the prompts to install drivers
5. Print a test page to verify

### Printing a Document

1. Open the document in any application
2. Press `Ctrl + P` or select **File → Print**
3. Select your printer
4. Configure options (copies, orientation, pages)
5. Click **Print**

### Managing Print Jobs

- **View queue**: Click the printer icon in the system tray
- **Cancel job**: Right-click a job → Cancel
- **Pause/resume**: Right-click → Pause/Resume printer

---

## Accessibility

EduOS is committed to accessibility. The following features are built in.

### Vision

| Feature | How to Enable | Description |
|---------|---------------|-------------|
| **Screen Reader** | System Settings → Accessibility → Screen Reader | Orca screen reader |
| **Magnifier** | `Meta + Alt + =` | Zoom in/out |
| **High Contrast** | `Meta + Alt + H` | High-contrast theme |
| **Large Text** | System Settings → Fonts → Force DPI | Scaling factor |
| **Color Blindness** | System Settings → Colors → Color Filters | Deuteranopia, protanopia, tritanopia filters |

### Hearing

| Feature | How to Enable | Description |
|---------|---------------|-------------|
| **Visual Alerts** | System Settings → Accessibility → Visual | Flash screen on alerts |
| **Closed Captions** | Per-application setting | Captions in media players |

### Mobility

| Feature | How to Enable | Description |
|---------|---------------|-------------|
| **Sticky Keys** | System Settings → Accessibility → Modifier Keys | Press one key at a time for shortcuts |
| **Slow Keys** | System Settings → Accessibility → Modifier Keys | Delay before key press registers |
| **Bounce Keys** | System Settings → Accessibility → Modifier Keys | Ignore accidental double-presses |
| **On-Screen Keyboard** | Keyboard icon in bottom panel | Virtual keyboard for touch/pointer input |
| **Voice Typing** | Available in text fields | Speech-to-text input |

### Applications with Accessibility Support

- **Learn Hub**: WCAG 2.1 AA compliant, screen-reader optimized
- **Exam Portal**: Keyboard-navigable, high-contrast exam mode
- **Dolphin**: File manager accessible via keyboard and screen reader

---

## Getting Help

### Built-in Help

| Resource | How to Access |
|----------|---------------|
| **KDE Help Center** | Application Menu → Help → Help Center |
| **EduOS Documentation** | Open `~/Documentation/` or visit `help://edos` |
| **Application Help** | Press `F1` in any application |
| **Manual Pages** | Open terminal and type `man <command>` |

### Online Resources

| Resource | URL |
|----------|-----|
| **EduOS Website** | https://edos.edu |
| **Documentation** | https://docs.edos.edu |
| **Community Forum** | https://community.edos.edu |
| **Knowledge Base** | https://support.edos.edu |
| **GitHub** | https://github.com/edos/edos |

### Reporting Issues

If you encounter problems:

1. **Application crashes**: A crash dialog will appear — click **Report** to send details
2. **System issues**: Open **Admin Center** → **Report Issue**
3. **Security vulnerabilities**: Email security@edos.edu (PGP-encrypted)

### Contacting Your Institution

For account issues, exam problems, or local support:

- **IT Help Desk**: Available from the system tray (question mark icon)
- **Faculty Advisor**: Contact through Learn Hub messaging
- **Exam Support**: During exams, use the **Help** button in Exam Portal

---

## Keyboard Shortcuts Reference

| Shortcut | Action |
|----------|--------|
| `Meta` | Application Menu |
| `Alt + F2` | Run command / Search |
| `Alt + Tab` | Switch windows |
| `Alt + Shift + Tab` | Switch windows (reverse) |
| `Ctrl + Alt + T` | Open terminal |
| `Meta + D` | Show desktop |
| `Meta + L` | Lock screen |
| `Meta + E` | Open file manager |
| `Meta + Arrow keys` | Tile window |
| `Print Screen` | Take screenshot |
| `Alt + Print Screen` | Screenshot of active window |
| `Ctrl + Alt + Del` | Log out / shut down |
| `Ctrl + F1-F4` | Switch virtual desktop |
| `Meta + Tab` | Switch virtual desktop |

---

*For additional assistance, contact your institution's IT support or visit https://support.edos.edu.*
