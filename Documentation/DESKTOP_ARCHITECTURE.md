# EduOS Desktop Architecture

## Overview

The EduOS desktop uses a Windows-style KDE Plasma 6.3.6 layout (Wayland).
It prioritizes discoverability and ease of use for students, teachers, and
administrators over visual novelty. All EduOS applications and branding
are fully preserved.

> **Note**: A macOS-inspired layout was previously implemented but reverted
> due to usability issues (hidden search, no app discovery, confusing
> navigation). The macOS dock remains available as an optional add-on.

## Layout

```
┌───────────────────────────────────────────────────────┐
│                                                       │
│    [Desktop with EduOS wallpaper + app shortcuts]      │
│                                                       │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 🏠 | 📝📚💻🔬🌐📁⚙️  🔔 Systray  🕐 Clock  ⬜  │ │  ← Full-width Taskbar
│  │ App | Pinned + Running Apps    Notifications    ▢  │ │
│  └──────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## Panel Architecture

### Top Panel (Containments[3])
| Property | Value |
|---|---|
| Plugin | `org.kde.panel` |
| Location | Top (`location=0`) |
| Floating | No |
| Alignment | Left |
| Width | 100% screen |
| Thickness | Default (thin) |

**Applets (left to right):**
| ID | Widget | Position | macOS equivalent |
|---|---|---|---|
| 31 | `org.kde.plasma.kickoff` | Far left | Apple menu |
| 35 | `org.kde.plasma.appmenu` | Next to Kickoff | App menu bar (File, Edit...) |
| 34 | `org.kde.plasma.panelspacer` | Expands to push | — |
| 33 | `org.kde.plasma.systemtray` | Right side | Menu bar extras |
| 32 | `org.kde.plasma.digitalclock` | Far right | Clock |

### Bottom Dock (Containments[2])
| Property | Value | macOS equivalent |
|---|---|---|---|
| Plugin | `org.kde.panel` | Dock |
| Location | Bottom (`location=4`) | Bottom |
| Floating | Yes (rounded corners + shadow) | Dock appearance |
| Auto-hide | Yes (`autohide=true`) | Dock hides when not needed |
| Alignment | Center | Centered icons |
| Width mode | Fit content (`lengthMode=2`) | Wraps to icons |
| Offset | 0 | Perfectly centered |

**Applets:**
| ID | Widget | Purpose |
|---|---|---|
| 5 | `org.kde.plasma.icontasks` | Icons-Only Task Manager (the dock) |
| 22 | `org.kde.plasma.showdesktop` | Minimize all / show desktop |

### System Tray Private (Containments[4])
Contains standard KDE system tray items: volume, network, bluetooth,
notifications, clipboard, devices, keyboard, battery, etc.

## Pinned Applications (Dock)

The following applications are pinned to the dock (in order):

1. **EduOS Demo Exam** (`eduos-demo-exam.desktop`)
2. **EduOS Learn Hub** (`eduos-learnhub.desktop`)
3. **EduOS Dev Suite** (`eduos-devsuite.desktop`)
4. **EduOS Cyber Lab** (`eduos-cyberlab.desktop`)
5. **Firefox** (`firefox-esr.desktop`)
6. **Files** (`org.kde.dolphin.desktop`)
7. **Settings** (`systemsettings.desktop`)

Running applications appear alongside pinned apps with an indicator dot.

## Visual Design

### Theme Stack
| Component | Choice | Purpose |
|---|---|---|
| Global Theme | BreezeDark | Modern dark appearance |
| Color Scheme | EduOS (custom) | Academic blue palette |
| Icon Theme | Papirus-Dark | Clean, modern icons |
| Window Decorations | Breeze | Rounded corners |
| Compositor | OpenGL, 60 FPS | Smooth animations |

### Animation Settings
| Parameter | Value | Effect |
|---|---|---|
| `AnimationSpeed` | 1 (Fast) | Quick, responsive feel |
| `MaxFps` | 60 | Smooth transitions |
| `WindowsBlockCompositing` | false | No compositor pauses |
| `UnredirectFullscreen` | true | Optimal fullscreen perf |

### Floating Dock Styling
- `floating=true` enables:
  - Rounded corners on the panel
  - Drop shadow beneath the panel
  - Visual separation from desktop content
- `alignment=center` with `lengthMode=2` makes the dock
  wrap to content width (only as wide as the icons)
- Semi-transparent background follows the BreezeDark theme

## User Coverage

## Desktop
- **Plugin**: `org.kde.desktopcontainment` — clean desktop background
- **No folder icons**: macOS-style clean desktop (unlike Windows)
- **Wallpaper**: EduOS branding via `/usr/share/wallpapers/eduos-wallpaper.png`

## User Coverage

| User | Layout Applied | Notes |
|---|---|---|
| jainam | ✅ | Currently active |
| student | ✅ | Next login |
| exam | ✅ | Next login |
| admin | ✅ | Next login |
| New users | ✅ via /etc/skel | Created automatically |

Configuration is stored in:
- `~/.config/plasma-org.kde.plasma.desktop-appletsrc` — Panel layout
- `~/.config/kwinrc` — Compositor & animations
- `~/.config/kdeglobals` — Color scheme & icons

## Performance Impact

### Memory
| Component | Before | After | Delta |
|---|---|---|---|
| plasmashell | ~170 MB (single panel) | ~310 MB (two panels) | +140 MB |
| Total system | ~2.4 GB / 3.8 GB | ~2.5 GB / 3.8 GB | Marginal |

The increase comes from running two panels instead of one, plus the
appmenu widget. Still well within budget (66% of 3.8 GB).

After fresh boot: plasmashell starts at ~65 MB and grows as widgets load.

### CPU
- Idle: <1% CPU (same as before)
- Animation: Smooth 60 FPS with OpenGL compositor
- No additional background processes or services

### Startup
- No new autostart entries created
- Uses only native Plasma 6 panels (no third-party dock software)
- Cold boot time unaffected (~9.5 seconds)

## Rollback

### Option 1: Run rollback commands (fastest)
```bash
# Restore panel layout
cp ~/.config/plasma-org.kde.plasma.desktop-appletsrc.eduos-backup \
   ~/.config/plasma-org.kde.plasma.desktop-appletsrc

# Restore KWin settings
cp ~/.config/kwinrc.eduos-backup ~/.config/kwinrc

# Restart Plasma shell
systemctl --user restart plasma-plasmashell.service
```

### Option 2: Re-run original Windows-style layout
```bash
# The original layout backup is at:
~/.config/plasma-org.kde.plasma.desktop-appletsrc.eduos-backup.ORIGINAL

# Or restore the first backup:
cp ~/.config/plasma-org.kde.plasma.desktop-appletsrc.eduos-backup \
   ~/.config/plasma-org.kde.plasma.desktop-appletsrc
```

### Option 3: Global rollback (all users)
```bash
sudo rm /usr/share/wallpapers/eduos-wallpaper.png
# Restore each user's config from backup if available
```

## Files Modified

| File | Purpose |
|---|---|
| `~/.config/plasma-org.kde.plasma.desktop-appletsrc` | Panel layout |
| `~/.config/kwinrc` | Compositor & animations |
| `~/.config/kdeglobals` | Theme, icons, colors |
| `/usr/share/wallpapers/eduos-wallpaper.png` | System wallpaper |
| `/etc/skel/.config/plasma-org.kde.plasma.desktop-appletsrc` | New user panel |
| `/etc/skel/.config/kwinrc` | New user compositor |
| `/etc/skel/.config/kdeglobals` | New user theme |
| `/etc/skel/.local/share/color-schemes/EduOS.colors` | New user colors |

## Scripts

| Script | Purpose | Run as |
|---|---|---|
| `~/EduOS/Scripts/eduos-desktop-layout.py` | Generate & apply layout | Current user |
| `~/EduOS/Scripts/eduos-apply-desktop-layout.sh` | Deploy to all users | root |

## Dock Solution Comparison

| Solution | Status | Reason |
|---|---|---|
| **Latte Dock** | ❌ Removed / unavailable | Unmaintained since 2022, no Plasma 6 support |
| **Cairo-Dock** | ❌ Not suitable | GTK-based, Wayland issues, heavy |
| **Plank** | ❌ Not suitable | X11 only, no Wayland support |
| **Native Plasma 6 Panel** | ✅ Selected | First-class Wayland support, optimized, KDE-native |
