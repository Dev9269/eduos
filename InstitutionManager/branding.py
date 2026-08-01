"""
EduOS Institution Manager — Branding Configuration
Allows institutions to customize logo, name, wallpaper, login screen, and welcome screen.
"""

import sys
from pathlib import Path
_DIR = Path(__file__).parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

import json
from pathlib import Path

from config import load_json, save_json, PATHS, log_activity
from styles import *


class BrandingManager:
    """Handles institution-level branding without modifying the OS."""

    def __init__(self):
        self.config = load_json(PATHS["branding"], self._defaults())

    def _defaults(self):
        return {
            "institution_name": "My Institution",
            "short_name": "MI",
            "logo_path": "",
            "wallpaper_path": "",
            "primary_color": PRIMARY,
            "secondary_color": PRIMARY_DARK,
            "login_message": "Welcome to EduOS",
            "welcome_title": "Welcome to EduOS",
            "welcome_subtitle": "Your Educational Operating System",
            "custom_css": "",
            "branding_active": True
        }

    def save(self):
        save_json(PATHS["branding"], self.config)
        self._apply_branding()
        log_activity("Branding Applied", f"Institution branding updated")

    def get_config(self):
        return self.config

    def update(self, **kwargs):
        self.config.update(kwargs)

    def set_logo(self, path):
        self.config["logo_path"] = path
        self.save()

    def set_wallpaper(self, path):
        self.config["wallpaper_path"] = path
        self.save()

    def _apply_branding(self):
        """Generate branding assets without modifying system files."""
        cfg = self.config
        name = cfg.get("institution_name", "Institution")
        short = cfg.get("short_name", "INS")
        primary = cfg.get("primary_color", PRIMARY)

        branding_dir = Path.home() / ".eduos" / "branding"
        branding_dir.mkdir(parents=True, exist_ok=True)

        # Generate login banner
        banner_html = f"""
        <div style="background: linear-gradient(135deg, {primary}, {cfg.get('secondary_color', PRIMARY_DARK)});
                    padding: 32px; border-radius: 16px; text-align: center;">
            <h1 style="color: white; font-size: 28px; margin: 0;">{name}</h1>
            <p style="color: rgba(255,255,255,0.8); font-size: 16px;">{cfg.get('login_message', 'Welcome')}</p>
        </div>
        """
        with open(branding_dir / "login_banner.html", "w") as f:
            f.write(banner_html)

        # Generate welcome screen config
        welcome = {
            "title": cfg.get("welcome_title", "Welcome"),
            "subtitle": cfg.get("welcome_subtitle", ""),
            "show_branding": True,
            "background_color": primary
        }
        with open(branding_dir / "welcome.json", "w") as f:
            json.dump(welcome, f, indent=2)

        return branding_dir

    def get_preview_html(self):
        cfg = self.config
        return f"""
        <div style="font-family: 'Inter', system-ui, sans-serif; max-width: 600px;">
            <div style="background: linear-gradient(135deg, {cfg['primary_color']}, {cfg['secondary_color']});
                        padding: 24px; border-radius: 12px; text-align: center;">
                <h1 style="color: white; font-size: 24px; margin: 0;">{cfg['institution_name']}</h1>
                <p style="color: rgba(255,255,255,0.8); font-size: 14px;">{cfg['welcome_subtitle']}</p>
            </div>
            <div style="padding: 16px; background: #f8fafc; border-radius: 8px; margin-top: 12px;">
                <p style="font-size: 13px; color: #64748b;">Login: "{cfg['login_message']}"</p>
                <p style="font-size: 12px; color: #94a3b8;">Short name: {cfg['short_name']}</p>
            </div>
        </div>
        """

    def deploy_branding(self):
        """Simulate deploying branding to all managed devices."""
        branding_dir = self._apply_branding()
        log_activity("Branding Deployed", f"Branding assets generated at {branding_dir}")
        return branding_dir
