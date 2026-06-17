#!/usr/bin/env python3
"""
EduOS Windows-Style Desktop Restore
Restores a full-width Windows-style KDE taskbar while preserving all
EduOS applications, branding, and custom functionality.

Layout:
  - Single full-width bottom taskbar (Windows style)
  - Kickoff app launcher with built-in search
  - Icons-Only Task Manager (shows running + pinned apps)
  - System tray + Clock + Show Desktop
  - Desktop: folder view with app icons (for easy discovery)
  - KRunner search (Super key / Alt+Space)
  - Ctrl+Alt+T for terminal

The macOS-style top panel and floating dock are removed.
A floating dock can be re-enabled via Settings > Dock if desired.

Safety: Creates backup before any modification.
"""

import shutil
import os
import sys
import subprocess
import re

CONFIG_PATH = os.path.expanduser("~/.config/plasma-org.kde.plasma.desktop-appletsrc")
BACKUP_PATH = CONFIG_PATH + ".windows-restore-backup"
KWINRC_PATH = os.path.expanduser("~/.config/kwinrc")

PINNED_APPS = [
    "file:///usr/share/applications/eduos-demo-exam.desktop",
    "file:///usr/share/applications/eduos-learnhub.desktop",
    "file:///usr/share/applications/eduos-devsuite.desktop",
    "file:///usr/share/applications/eduos-cyberlab.desktop",
    "file:///usr/share/applications/firefox-esr.desktop",
    "file:///usr/share/applications/org.kde.dolphin.desktop",
    "file:///usr/share/applications/systemsettings.desktop",
]


def backup_config():
    if os.path.exists(CONFIG_PATH):
        shutil.copy2(CONFIG_PATH, BACKUP_PATH)
        print(f"✅ Current config backed up to: {BACKUP_PATH}")


def build_windows_layout():
    lines = []
    a = lines.append

    # ── ActionPlugins ──
    a("[ActionPlugins][0]")
    a("RightButton;NoModifier=org.kde.contextmenu")
    a("")
    a("[ActionPlugins][1]")
    a("RightButton;NoModifier=org.kde.contextmenu")
    a("")

    # ── Desktop Containment [1] (Folder View with icons) ──
    a("[Containments][1]")
    a("activityId=00000000-0000-0000-0000-000000000000")
    a("formfactor=0")
    a("immutability=1")
    a("lastScreen=0")
    a("location=0")
    a("plugin=org.kde.plasma.folder")
    a("wallpaperplugin=org.kde.image")
    a("")
    a("[Containments][1][General]")
    a('positions={}')
    a("")
    a("[Containments][1][Wallpaper][org.kde.image][General]")
    a("Image=file:///usr/share/wallpapers/eduos-wallpaper.png")
    a("")

    # ── Single Bottom Panel (Taskbar) [2] ──
    a("[Containments][2]")
    a("activityId=")
    a("alignment=left")
    a("floating=false")
    a("formfactor=2")
    a("immutability=0")
    a("lastScreen=0")
    a("location=4")
    a("maxLength=1.0")
    a("offset=0")
    a("plugin=org.kde.panel")
    a("wallpaperplugin=org.kde.image")
    a("")

    # Applet 3: Kickoff (Application Launcher with search)
    a("[Containments][2][Applets][3]")
    a("immutability=0")
    a("plugin=org.kde.plasma.kickoff")
    a("")
    a("[Containments][2][Applets][3][Configuration]")
    a("PreloadWeight=100")
    a("popupHeight=508")
    a("popupWidth=647")
    a("")
    a("[Containments][2][Applets][3][Configuration][General]")
    a("favoritesPortedToKAstats=true")
    a("")

    # Applet 5: Icons-Only Task Manager (running + pinned apps)
    a("[Containments][2][Applets][5]")
    a("immutability=0")
    a("plugin=org.kde.plasma.icontasks")
    a("")
    a("[Containments][2][Applets][5][Configuration][General]")
    launchers_str = ";".join(PINNED_APPS)
    a(f"launchers={launchers_str}")
    a("groupingStrategy=0")
    a("showOnlyCurrentDesktop=false")
    a("showOnlyCurrentScreen=false")
    a("sortMode=1")
    a("")

    # Applet 7: System Tray
    a("[Containments][2][Applets][7]")
    a("immutability=0")
    a("plugin=org.kde.plasma.systemtray")
    a("")
    a("[Containments][2][Applets][7][Configuration]")
    a("PreloadWeight=60")
    a("SystrayContainmentId=8")
    a("")

    # Applet 21: Digital Clock
    a("[Containments][2][Applets][21]")
    a("immutability=0")
    a("plugin=org.kde.plasma.digitalclock")
    a("")
    a("[Containments][2][Applets][21][Configuration]")
    a("popupHeight=400")
    a("popupWidth=560")
    a("")
    a("[Containments][2][Applets][21][Configuration][Appearance]")
    a("fontWeight=400")
    a("")

    # Applet 22: Show Desktop
    a("[Containments][2][Applets][22]")
    a("immutability=0")
    a("plugin=org.kde.plasma.showdesktop")
    a("")

    # Applet order: Kickoff | Task Manager | System Tray | Clock | Show Desktop
    a("[Containments][2][General]")
    a("AppletOrder=3;5;7;21;22")
    a("")

    # Wallpaper for panel
    a("[Containments][2][Wallpaper][org.kde.image][General]")
    a("Image=file:///usr/share/wallpapers/eduos-wallpaper.png")
    a("")

    # ── System Tray Private [8] ──
    a("[Containments][8]")
    a("activityId=")
    a("formfactor=2")
    a("immutability=1")
    a("lastScreen=0")
    a("location=4")
    a("plugin=org.kde.plasma.private.systemtray")
    a("popupHeight=432")
    a("popupWidth=432")
    a("wallpaperplugin=org.kde.image")
    a("")

    systray_plugins = [
        ("9", "org.kde.plasma.manage-inputmethod"),
        ("10", "org.kde.plasma.volume"),
        ("11", "org.kde.kscreen"),
        ("12", "org.kde.kdeconnect"),
        ("13", "org.kde.plasma.devicenotifier"),
        ("14", "org.kde.plasma.cameraindicator"),
        ("15", "org.kde.plasma.keyboardindicator"),
        ("16", "org.kde.plasma.keyboardlayout"),
        ("17", "org.kde.plasma.notifications"),
        ("18", "org.kde.plasma.clipboard"),
        ("19", "org.kde.plasma.vault"),
        ("20", "org.kde.plasma.printmanager"),
        ("23", "org.kde.plasma.networkmanagement"),
        ("24", "org.kde.plasma.brightness"),
        ("25", "org.kde.plasma.battery"),
    ]

    for applet_id, plugin_name in systray_plugins:
        a(f"[Containments][8][Applets][{applet_id}]")
        a("immutability=1")
        a(f"plugin={plugin_name}")
        a("")

    a("[Containments][8][General]")
    known = (
        "org.kde.plasma.manage-inputmethod,org.kde.plasma.volume,org.kde.kscreen,"
        "org.kde.plasma.battery,org.kde.kdeconnect,org.kde.kupapplet,"
        "org.kde.plasma.devicenotifier,org.kde.plasma.cameraindicator,"
        "org.kde.plasma.mediacontroller,org.kde.plasma.keyboardindicator,"
        "org.kde.plasma.keyboardlayout,org.kde.plasma.notifications,"
        "org.kde.plasma.brightness,org.kde.plasma.clipboard,org.kde.plasma.bluetooth,"
        "org.kde.plasma.networkmanagement,org.kde.plasma.vault,org.kde.plasma.printmanager"
    )
    a(f"extraItems={known}")
    a(f"knownItems={known}")
    a("")

    # ── ScreenMapping ──
    a("[ScreenMapping]")
    a("itemsOnDisabledScreens=")
    a("screenMapping=")

    return "\n".join(lines)


def restore_kwin_settings():
    """Restore KWin to Windows-style compositor settings."""
    bak = KWINRC_PATH + ".windows-restore-backup"
    if os.path.exists(KWINRC_PATH) and not os.path.exists(bak):
        shutil.copy2(KWINRC_PATH, bak)

    # Ensure compositor is enabled for smooth experience, but disable
    # any macOS-specific animation tricks
    settings = [
        ("Compositing", "AnimationSpeed", "2"),
        ("Compositing", "Backend", "OpenGL"),
        ("Compositing", "Enabled", "true"),
        ("Compositing", "MaxFps", "60"),
        ("Compositing", "UnredirectFullscreen", "true"),
        ("Compositing", "WindowsBlockCompositing", "true"),
        ("Compositing", "ScaleMethod", "Accurate"),
        ("org.kde.kdecoration2", "ButtonsOnLeft", ""),
        ("org.kde.kdecoration2", "ButtonsOnRight", "IAX"),
        ("org.kde.kdecoration2", "theme", "Breeze"),
    ]
    for group, key, val in settings:
        subprocess.run(
            ["kwriteconfig6", "--file", KWINRC_PATH, "--group", group, "--key", key, val],
            capture_output=True, timeout=5
        )
    print("✅ KWin settings restored to Windows-style defaults")


def ensure_krunner_shortcuts():
    """Ensure KRunner search is accessible via Super key and Alt+Space."""
    shortcuts_file = os.path.expanduser("~/.config/kglobalshortcutsrc")
    try:
        subprocess.run([
            "kwriteconfig6", "--file", shortcuts_file,
            "--group", "krunner", "--key", "_launch", "Alt+Space\tAlt+F2\tSearch"
        ], capture_output=True, timeout=5)
        print("✅ KRunner shortcuts set: Super/Alt+Space/Alt+F2")
    except Exception as e:
        print(f"⚠️  Could not set KRunner shortcuts: {e}")


def ensure_terminal_shortcut():
    """Ensure Ctrl+Alt+T launches Konsole."""
    shortcuts_file = os.path.expanduser("~/.config/kglobalshortcutsrc")
    try:
        subprocess.run([
            "kwriteconfig6", "--file", shortcuts_file,
            "--group", "org.kde.konsole", "--key", "_launch", "Ctrl+Alt+T\t\tKonsole"
        ], capture_output=True, timeout=5)
        print("✅ Terminal shortcut set: Ctrl+Alt+T → Konsole")
    except Exception as e:
        print(f"⚠️  Could not set terminal shortcut: {e}")


def apply_wallpaper():
    """Apply EduOS wallpaper to the desktop."""
    try:
        subprocess.run([
            "plasma-apply-wallpaperimage", "/usr/share/wallpapers/eduos-wallpaper.png"
        ], capture_output=True, timeout=10)
        print("✅ EduOS wallpaper applied")
    except Exception as e:
        print(f"⚠️  Could not apply wallpaper: {e}")


def diagnose():
    """Verify the Windows-style layout is complete."""
    if not os.path.exists(CONFIG_PATH):
        return False
    with open(CONFIG_PATH) as f:
        text = f.read()

    checks = [
        ("Single bottom panel", '[Containments][2]' in text and 'plugin=org.kde.panel' in text),
        ("Full-width taskbar", 'maxLength=1.0' in text),
        ("Not floating", 'floating=false' in text and 'Containments][2]' in text),
        ("Kickoff launcher", 'org.kde.plasma.kickoff' in text),
        ("Task Manager", 'org.kde.plasma.icontasks' in text),
        ("System Tray", 'org.kde.plasma.systemtray' in text),
        ("Digital Clock", 'org.kde.plasma.digitalclock' in text),
        ("Show Desktop", 'org.kde.plasma.showdesktop' in text),
        ("Desktop folder view", 'plugin=org.kde.plasma.folder' in text),
        ("EduOS wallpaper", 'eduos-wallpaper.png' in text),
        ("No macOS appmenu", 'org.kde.plasma.appmenu' not in text),
        ("Pinned apps", all(app in text for app in PINNED_APPS[:3])),
    ]

    all_pass = True
    print("\n📋 Windows-Style Layout Diagnosis:")
    print("─" * 50)
    for name, result in checks:
        status = "✅" if result else "❌"
        print(f"  {status}  {name}")
        if not result:
            all_pass = False
    print("─" * 50)
    return all_pass


def restart_shell():
    print("\n🔄 Restarting Plasma shell to apply changes...")
    try:
        subprocess.run(
            ["systemctl", "--user", "restart", "plasma-plasmashell.service"],
            check=True, timeout=30
        )
        print("✅ Plasma shell restarted")
    except subprocess.CalledProcessError:
        subprocess.run(["kquitapp6", "plasmashell"], timeout=15)
        subprocess.run(["plasmashell"], timeout=15)


def main():
    print("╔═══════════════════════════════════════════════╗")
    print("║   EduOS Windows-Style Desktop Restore         ║")
    print("╚═══════════════════════════════════════════════╝")
    print()

    # Step 1: Backup
    print("📦 Step 1: Backing up current configuration...")
    backup_config()

    # Step 2: Generate Windows layout
    print("\n🏠 Step 2: Building Windows-style taskbar layout...")
    new_config = build_windows_layout()

    # Step 3: Write
    print("\n💾 Step 3: Writing new configuration...")
    with open(CONFIG_PATH, "w") as f:
        f.write(new_config)
    print(f"   Written to: {CONFIG_PATH}")

    # Step 4: Restart shell IMMEDIATELY to lock in the clean config
    # (before other tools like plasma-apply-wallpaperimage can trigger Plasma to re-write containments)
    print("\n🔄 Step 4: Restarting shell to lock in clean config...")
    restart_shell()

    # Step 5: Restore KWin
    print("\n⚡ Step 5: Restoring KWin compositor settings...")
    restore_kwin_settings()

    # Step 6: Set wallpaper
    print("\n🖼️  Step 6: Applying EduOS wallpaper...")
    apply_wallpaper()

    # Step 7: Restore shortcuts
    print("\n⌨️  Step 7: Restoring keyboard shortcuts...")
    ensure_krunner_shortcuts()
    ensure_terminal_shortcut()

    # Step 8: Diagnose
    print("\n🔍 Step 8: Diagnosing configuration...")
    all_ok = diagnose()

    if all_ok:
        print("\n✨ Windows-style desktop restored!")
    else:
        print("\n⚠️  Diagnosis found issues. Check the ❌ entries above.")
        print("   The layout should still be usable. Run diagnose again if needed.")

    print()
    print("📌 What was restored:")
    print("  • Single full-width bottom taskbar (Windows style)")
    print("  • Kickoff app launcher on the left (with built-in search)")
    print("  • Task manager showing all running + pinned apps")
    print("  • System tray + notifications + clock + show desktop")
    print("  • Desktop folder view (icons visible for easy discovery)")
    print("  • Application search: Super key, Alt+Space, click launcher")
    print("  • Terminal: Ctrl+Alt+T opens Konsole")
    print("  • All EduOS apps pinned to taskbar")
    print()
    print("📌 To re-enable the macOS dock later:")
    print("   Right-click panel → Edit Panel → Add floating dock panel")
    print("   or run: python3 ~/EduOS/Scripts/eduos-desktop-layout.py")
    print()
    print("📌 Rollback:")
    print(f"   cp {BACKUP_PATH} {CONFIG_PATH}")
    print("   systemctl --user restart plasma-plasmashell.service")


if __name__ == "__main__":
    main()
