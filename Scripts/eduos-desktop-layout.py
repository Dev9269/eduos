#!/usr/bin/env python3
"""
EduOS Desktop Layout Transformation
Transforms KDE Plasma 6 desktop into a macOS-inspired hybrid design
while preserving all existing EduOS applications and functionality.

Layout:
  - Desktop: Clean wallpaper (no folder icons) - macOS style
  - Top panel: App Launcher + App Menu Bar + Spacer + Systray + Clock
  - Bottom dock: Centered floating autohide Icons-Only Task Manager

Safety: Creates backup before any modification.
Uses direct text generation to handle KDE QSettings multi-level format.
"""

import re
import shutil
import os
import sys
import subprocess

CONFIG_PATH = os.path.expanduser("~/.config/plasma-org.kde.plasma.desktop-appletsrc")
BACKUP_PATH = CONFIG_PATH + ".eduos-backup"
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
        print(f"✅ Backed up current config to: {BACKUP_PATH}")


def restore_backup():
    if os.path.exists(BACKUP_PATH):
        shutil.copy2(BACKUP_PATH, CONFIG_PATH)
        print("✅ Restored from backup.")


def build_new_config():
    """
    Build the new plasma config as raw text (KDE QSettings format).
    We preserve the desktop containment [Containments][1] but completely
    replace everything else with the two-panel layout.
    """

    # Read existing config to preserve desktop wallpaper
    existing_text = ""
    existing_wallpaper = "file:///usr/share/wallpapers/eduos-wallpaper.png"
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            existing_text = f.read()
        # Extract wallpaper path from existing config
        m = re.search(
            r'\[Containments\]\[1\]\[Wallpaper\]\[org\.kde\.image\]\[General\][^\[]+Image=([^\n]+)',
            existing_text
        )
        if m:
            existing_wallpaper = m.group(1).strip()

    lines = []
    a = lines.append

    # ── ActionPlugins ──
    a("[ActionPlugins][0]")
    a("RightButton;NoModifier=org.kde.contextmenu")
    a("")
    a("[ActionPlugins][1]")
    a("RightButton;NoModifier=org.kde.contextmenu")
    a("")

    # ── Desktop Containment [1] with clean background (macOS style) ──
    # We write this explicitly so the wallpaper is set from the start.
    # Using org.kde.plasma.folder without icons is the most stable desktop.
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
    a(f"[Containments][1][Wallpaper][org.kde.image][General]")
    a(f"Image={existing_wallpaper}")
    a("")

    # ── Bottom Panel (Dock) [2] - macOS style floating autohide dock ──
    a("[Containments][2]")
    a("activityId=")
    a("alignment=center")
    a("autohide=true")
    a("floating=true")
    a("formfactor=2")
    a("immutability=0")
    a("lastScreen=0")
    a("lengthMode=2")
    a("location=4")
    a("maxLength=0.6")
    a("offset=0")
    a("plugin=org.kde.panel")
    a("wallpaperplugin=org.kde.image")
    a("")

    # Icons-Only Task Manager (dock)
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

    # Show Desktop button
    a("[Containments][2][Applets][22]")
    a("immutability=0")
    a("plugin=org.kde.plasma.showdesktop")
    a("")

    # Applet order
    a("[Containments][2][General]")
    a("AppletOrder=5;22")
    a("")

    # ── Top Panel (Menu Bar) [3] - macOS style thin dark menu bar ──
    a("[Containments][3]")
    a("activityId=")
    a("alignment=left")
    a("floating=false")
    a("formfactor=2")
    a("immutability=0")
    a("lastScreen=0")
    a("location=0")
    a("maxLength=1.0")
    a("offset=0")
    a("panelSize=28")
    a("plugin=org.kde.panel")
    a("wallpaperplugin=org.kde.image")
    a("")

    # Kickoff (Application Launcher) - macOS Apple menu equivalent
    a("[Containments][3][Applets][31]")
    a("immutability=0")
    a("plugin=org.kde.plasma.kickoff")
    a("")
    a("[Containments][3][Applets][31][Configuration]")
    a("PreloadWeight=100")
    a("popupHeight=508")
    a("popupWidth=647")
    a("")
    a("[Containments][3][Applets][31][Configuration][General]")
    a("favoritesPortedToKAstats=true")
    a("")

    # Application Menu Bar - macOS global menu (shows app menus in top bar)
    a("[Containments][3][Applets][35]")
    a("immutability=0")
    a("plugin=org.kde.plasma.appmenu")
    a("")
    a("[Containments][3][Applets][35][Configuration][General]")
    a("showButtonBackgrounds=false")
    a("showExtraItems=false")
    a("showMenuTitleOnButton=true")
    a("")

    # Panel Spacer - pushes right-side items to the right
    a("[Containments][3][Applets][34]")
    a("immutability=0")
    a("plugin=org.kde.plasma.panelspacer")
    a("")

    # System Tray - right side
    a("[Containments][3][Applets][33]")
    a("immutability=0")
    a("plugin=org.kde.plasma.systemtray")
    a("")
    a("[Containments][3][Applets][33][Configuration]")
    a("PreloadWeight=60")
    a("SystrayContainmentId=4")
    a("")

    # Digital Clock - far right (compact, time only like macOS)
    a("[Containments][3][Applets][32]")
    a("immutability=0")
    a("plugin=org.kde.plasma.digitalclock")
    a("")
    a("[Containments][3][Applets][32][Configuration]")
    a("popupHeight=400")
    a("popupWidth=560")
    a("")
    a("[Containments][3][Applets][32][Configuration][Appearance]")
    a("fontWeight=400")
    a("showDate=false")
    a("showSeconds=false")
    a("")

    # Applet order (left to right): Kickoff | AppMenu | Spacer | Systray | Clock
    a("[Containments][3][General]")
    a("AppletOrder=31;35;34;33;32")
    a("")

    # ── System Tray Private [4] ──
    a("[Containments][4]")
    a("activityId=")
    a("formfactor=2")
    a("immutability=1")
    a("lastScreen=0")
    a("location=0")
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
        a(f"[Containments][4][Applets][{applet_id}]")
        a("immutability=1")
        a(f"plugin={plugin_name}")
        a("")

    a("[Containments][4][General]")
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


def set_desktop_wallpaper():
    """Verify the EduOS wallpaper is in the config (set during config generation)."""
    wallpaper_path = "file:///usr/share/wallpapers/eduos-wallpaper.png"
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            content = f.read()
        if wallpaper_path in content:
            print(f"   ✅ EduOS wallpaper already in config")
        else:
            # Fallback: append wallpaper to any desktop containment
            desktop_id = None
            for m in re.finditer(r'\[Containments\]\[(\d+)\]', content):
                cid = m.group(1)
                end = content.find('\n[', m.start() + 1)
                if end == -1:
                    end = len(content)
                section = content[m.start():end]
                if 'formfactor=0' in section:
                    desktop_id = cid
                    break
            if desktop_id:
                with open(CONFIG_PATH, "a") as f:
                    f.write(f"\n[Containments][{desktop_id}][Wallpaper][org.kde.image][General]\n")
                    f.write(f"Image={wallpaper_path}\n")
                print(f"   ✅ Wallpaper appended for desktop containment [{desktop_id}]")
            else:
                print(f"   ⚠️  No desktop containment found to set wallpaper")


def apply_kwin_settings():
    """Set KWin animation and compositor settings for smooth macOS-style feel."""
    bak = KWINRC_PATH + ".eduos-backup"
    if os.path.exists(KWINRC_PATH) and not os.path.exists(bak):
        shutil.copy2(KWINRC_PATH, bak)

    for group, key, val in [
        ("Compositing", "AnimationSpeed", "1"),
        ("Compositing", "Backend", "OpenGL"),
        ("Compositing", "Enabled", "true"),
        ("Compositing", "MaxFps", "60"),
        ("Compositing", "UnredirectFullscreen", "true"),
        ("Compositing", "WindowsBlockCompositing", "False"),
        ("Compositing", "ScaleMethod", "Accurate"),
        ("org.kde.kdecoration2", "ButtonsOnLeft", ""),
        ("org.kde.kdecoration2", "ButtonsOnRight", "IAX"),
        ("org.kde.kdecoration2", "theme", "Breeze"),
    ]:
        cmd = ["kwriteconfig6", "--file", KWINRC_PATH, "--group", group, "--key", key, val]
        subprocess.run(cmd, capture_output=True, timeout=5)

    print("✅ Updated KWin compositor settings")
    print("   • Animation speed: Fast (1)")
    print("   • Compositor: OpenGL 60 FPS")
    print("   • Window decorations: Breeze (modern rounded corners)")


def diagnose():
    """Verify the generated config is complete."""
    if not os.path.exists(CONFIG_PATH):
        return False
    with open(CONFIG_PATH) as f:
        text = f.read()

    checks = [
        ("Bottom dock", '[Containments][2]' in text and 'plugin=org.kde.panel' in text),
        ("Floating enabled", 'floating=true' in text),
        ("Centered alignment", 'Containments][2]' in text and 'alignment=center' in text),
        ("Icontasks widget", 'org.kde.plasma.icontasks' in text),
        ("Show Desktop", 'org.kde.plasma.showdesktop' in text),
        ("Top panel", '[Containments][3]' in text and 'location=0' in text),
        ("App Menu Bar", 'org.kde.plasma.appmenu' in text),
        ("Kickoff launcher", 'org.kde.plasma.kickoff' in text),
        ("System tray", 'org.kde.plasma.systemtray' in text),
        ("Digital clock", 'org.kde.plasma.digitalclock' in text),
        ("Pinned apps", all(app in text for app in PINNED_APPS[:3])),
        ("Systray private", 'org.kde.plasma.private.systemtray' in text),
    ]

    all_pass = True
    print("\n📋 Layout Diagnosis:")
    print("─" * 50)
    for name, result in checks:
        status = "✅" if result else "❌"
        print(f"  {status}  {name}")
        if not result:
            all_pass = False
    print("─" * 50)
    return all_pass


def set_wallpaper_after_restart():
    """Set the EduOS wallpaper after Plasma shell restart (desktop ID may change)."""
    wallpaper_path = "file:///usr/share/wallpapers/eduos-wallpaper.png"
    try:
        subprocess.run(
            ["plasma-apply-wallpaperimage", "/usr/share/wallpapers/eduos-wallpaper.png"],
            capture_output=True, timeout=10
        )
        print("   ✅ Wallpaper applied via plasma-apply-wallpaperimage")
    except Exception:
        # Fallback: use DBus to set wallpaper for all desktops
        try:
            subprocess.run([
                "qdbus6", "org.kde.plasmashell", "/PlasmaShell",
                "org.kde.PlasmaShell.setWallpaper",
                "org.kde.image",
                f"{{'Image': 'file:///usr/share/wallpapers/eduos-wallpaper.png'}}",
                "0"
            ], capture_output=True, timeout=10)
            print("   ✅ Wallpaper applied via DBus")
        except Exception as e2:
            print(f"   ⚠️  Could not apply wallpaper: {e2}")


def restart_shell():
    print("\n🔄 Restarting Plasma shell to apply changes...")
    try:
        subprocess.run(
            ["systemctl", "--user", "restart", "plasma-plasmashell.service"],
            check=True, timeout=30
        )
        print("✅ Plasma shell restarted via systemd")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  systemd restart failed ({e}), trying kquitapp6...")
        try:
            subprocess.run(["kquitapp6", "plasmashell"], check=True, timeout=15)
        except Exception:
            pass
        subprocess.run(["plasmashell", "--no-respawn"], check=True, timeout=15)


def main():
    print("╔══════════════════════════════════════════════╗")
    print("║    EduOS Desktop Transformation (Phase 3)    ║")
    print("╚══════════════════════════════════════════════╝")
    print()

    # Step 1: Backup
    print("📦 Step 1: Backing up current configuration...")
    backup_config()

    # Step 2: Generate new config
    print("\n🎨 Step 2: Generating macOS-inspired hybrid layout...")
    new_config = build_new_config()

    # Step 3: Write
    print("\n💾 Step 3: Writing new configuration...")
    with open(CONFIG_PATH, "w") as f:
        f.write(new_config)
    print(f"   Written to: {CONFIG_PATH}")

    # Step 4: Set wallpaper
    print("\n🖼️  Step 4: Setting desktop wallpaper...")
    set_desktop_wallpaper()

    # Step 5: KWin settings
    print("\n⚡ Step 5: Applying visual & animation settings...")
    apply_kwin_settings()

    # Step 6: Diagnose
    print("\n🔍 Step 6: Diagnosing configuration...")
    all_ok = diagnose()

    if all_ok:
        # Step 7: Restart
        restart_shell()

        # Step 8: After restart, set wallpaper (Plasma may have created a new desktop containment)
        print("\n🖼️  Step 8: Setting wallpaper on active desktop...")
        set_wallpaper_after_restart()
        print("\n✨ Desktop transformation complete!")
    else:
        print("\n⚠️  Diagnosis found issues. Restoring backup...")
        restore_backup()
        sys.exit(1)

    print()
    print("📌 New Layout (macOS format):")
    print("  ┌───────────────────────────────────────────────┐")
    print("  │  🏠 App Menu | File Edit View   🔔 Systray 🕐 │  ← Menu bar")
    print("  ├───────────────────────────────────────────────┤")
    print("  │                                               │")
    print("  │           [Clean Desktop - No Icons]           │")
    print("  │                                               │")
    print("  │       ┌──────────────────────────┐            │")
    print("  │       │  📝📚💻🔬🌐📁⚙️   ⬜    │            │  ← Floating Dock")
    print("  │       └──────────────────────────┘            │")
    print("  └───────────────────────────────────────────────┘")
    print()
    print("📌 Rollback:")
    print("   cp ~/.config/plasma-org.kde.plasma.desktop-appletsrc.eduos-backup ~/.config/plasma-org.kde.plasma.desktop-appletsrc")
    print("   cp ~/.config/kwinrc.eduos-backup ~/.config/kwinrc")
    print("   systemctl --user restart plasma-plasmashell.service")


if __name__ == "__main__":
    main()
