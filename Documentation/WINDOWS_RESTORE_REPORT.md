# EduOS Windows Desktop Restore Report

## Summary

The macOS-inspired redesign was reverted in favor of a stable Windows-style
desktop layout. All EduOS applications, branding, and custom functionality
are preserved.

## Settings Restored

| Setting | Value | Effect |
|---|---|---|
| Panel location | Bottom (location=4) | Full-width Windows taskbar |
| Panel floating | false | Solid, non-transparent taskbar |
| Panel width | 100% (maxLength=1.0) | Full screen width |
| Alignment | left | Content flows from left |
| Desktop plugin | org.kde.plasma.folder | Desktop shows icons |
| Compositing | enabled | Smooth visuals |
| AnimationSpeed | 2 (Normal) | Responsive, not sluggish |

## KDE Components Restored

| Component | Location | Purpose |
|---|---|---|
| **Kickoff** (App Launcher) | Taskbar, far left | Click to browse/search all apps |
| **Icons-Only Task Manager** | Taskbar, next to launcher | Shows running + pinned apps |
| **System Tray** | Taskbar, right side | Network, sound, battery, notifications |
| **Digital Clock** | Taskbar, far right | Time display |
| **Show Desktop** | Taskbar, far right | Minimize all windows |
| **Desktop Folder View** | Full desktop | Application shortcut icons |
| **KRunner** | Alt+Space / Super key | Universal search |

## Components Removed

| Component | Reason |
|---|---|
| macOS App Menu Bar (appmenu) | Confusing, no search, hard to discover |
| Thin top panel (panelSize=28) | Too small for taskbar use |
| Floating bottom dock (autohide) | Hidden by default, not discoverable |
| WindowDecoration adjustments | Restored to Breeze defaults |

## Search Functionality Status

| Method | Status | Notes |
|---|---|---|
| **Kickoff menu search** | ✅ Working | Click launcher, start typing |
| **Super key** (Windows key) | ✅ Working | Opens KRunner search overlay |
| **Alt+Space** | ✅ Working | Opens KRunner search overlay |
| **Alt+F2** | ✅ Working | Opens KRunner command dialog |

### Verified searches work:
- `Konsole` → Terminal app appears
- `Firefox` → Browser appears
- `EduOS Exam Portal` → Exam app appears
- `Learn Hub` → Learn Hub appears
- `Dev Suite` → Dev Suite appears
- `Cyber Lab` → Cyber Lab appears
- `Admin Center` → Admin Center appears

## Launcher Functionality Status

| Method | Status |
|---|---|
| Click Kickoff icon on taskbar | ✅ Opens full application menu |
| Type in Kickoff search box | ✅ Filters applications instantly |
| Browse categories in Kickoff | ✅ All apps organized by category |
| Click desktop shortcut | ✅ All EduOS apps have desktop icons |

## Terminal Accessibility Status

| Method | Status | Notes |
|---|---|---|
| **Ctrl+Alt+T** | ✅ Working | Opens Konsole immediately |
| Search for "Konsole" | ✅ Working | Shows in Kickoff and KRunner |
| Desktop shortcut "Terminal" | ✅ Working | On Desktop as Konsole icon |
| Application menu → Terminal | ✅ Found under "System" category |

## Desktop Icons Available (for all users)

The following shortcuts are placed on the Desktop for instant access:

- **EduOS Demo Exam** — Full demo examination application
- **EduOS Learn Hub** — Web-based learning portal (port 5050)
- **EduOS Dev Suite** — Development tools launcher
- **EduOS Cyber Lab** — Docker-based security labs
- **EduOS Admin Center** — Campus management console
- **EduOS Exam Mode** — Production exam application
- **EduOS Welcome** — First-run wizard
- **Firefox** — Web browser
- **Files** — Dolphin file manager
- **Terminal** — Konsole terminal emulator
- **Settings** — System settings

## Broken Configurations Found

1. **macOS appmenu leaked into restore**: When the config was written and the
   wallpaper tool ran before restart, Plasma re-serialized old containment
   IDs. Fixed by restarting Plasma shell immediately after writing config.

2. **Desktop containment ID changed on every restart**: Plasma 6 does not
   preserve a fixed desktop containment ID. Wallpaper must be applied via
   `plasma-apply-wallpaperimage` after restart.

3. **kwriteconfig6 cannot handle nested QSettings keys**: The `][` characters
   in group names like `[Containments][3]` are mangled by kwriteconfig6 into
   `[Containments\x5d\x5b3]`. Config sections must be written as raw text.

## User Coverage

| User | Config | Desktop Icons | Search | Terminal |
|---|---|---|---|---|
| jainam | ✅ | 11 shortcuts | ✅ | ✅ |
| student | ✅ | 13 shortcuts | ✅ | ✅ |
| exam | ✅ | 12 shortcuts | ✅ | ✅ |
| admin | ✅ | 12 shortcuts | ✅ | ✅ |
| New users | ✅ via /etc/skel | ✅ via /etc/skel | ✅ | ✅ |

## macOS Dock — Now Optional

The macOS-style floating dock has been **removed as the primary navigation**.
Users who want a dock can re-enable it:

```
Right-click panel → Edit Mode → Add Panel → "Add Floating Dock"
```
or run the old script:
```
python3 ~/EduOS/Scripts/eduos-desktop-layout.py
```

The Windows-style taskbar is the default and only active layout.

## Files Modified

| File | Purpose |
|---|---|
| `~/EduOS/Scripts/eduos-restore-windows-layout.py` | Windows layout generator |
| `~/EduOS/Scripts/eduos-apply-desktop-layout.sh` | Multi-user deployer |
| `~/EduOS/Documentation/WINDOWS_RESTORE_REPORT.md` | This report |
| `~/.config/plasma-org.kde.plasma.desktop-appletsrc` | Panel layout |
| `~/.config/kwinrc` | Compositor settings |
| `~/.config/kglobalshortcutsrc` | KRunner + Terminal shortcuts |
| `~/Desktop/*.desktop` (all users) | App shortcut icons |

## Rollback

To restore the macOS layout:
```bash
cp ~/.config/plasma-org.kde.plasma.desktop-appletsrc.windows-restore-backup \
   ~/.config/plasma-org.kde.plasma.desktop-appletsrc
systemctl --user restart plasma-plasmashell.service
```

Or re-run the macOS layout script:
```bash
python3 ~/EduOS/Scripts/eduos-desktop-layout.py
```

## Quick Verification

To verify the Windows layout is active:
```bash
# Check panel count (should be 1)
grep -c 'plugin=org.kde.panel' ~/.config/plasma-org.kde.plasma.desktop-appletsrc

# Check no macOS appmenu (should be 0)
grep -c 'appmenu' ~/.config/plasma-org.kde.plasma.desktop-appletsrc

# Check taskbar is full width and not floating
grep -E 'floating|maxLength' ~/.config/plasma-org.kde.plasma.desktop-appletsrc

# Test search
qdbus6 org.kde.krunner /App org.kde.krunner.App.query "Konsole"

# Test terminal shortcut
kwriteconfig6 --file ~/.config/kglobalshortcutsrc --group org.kde.konsole --key "_launch"
```

## Recommendations for Future UI Changes

1. **Always restart shell before applying wallpaper/tools** — Avoids
   Plasma re-serializing old containment data.

2. **Never use kwriteconfig6 for nested QSettings keys** — Use raw text
   file generation for `plasma-org.kde.plasma.desktop-appletsrc`.

3. **Test with a non-admin user** before deploying to all users — The
   `exam` user's restricted shell could break if panel layout removes
   essential widgets.

4. **Keep desktop folder view enabled** for educational environments —
   First-year students find apps faster when they can see icons on the
   desktop.

5. **Dock should always be optional** — Power users can add a dock,
   but the default must be the standard taskbar for beginners.

6. **Backup before every layout change** — The config file is fragile
   and a single bad write can break the entire desktop.
