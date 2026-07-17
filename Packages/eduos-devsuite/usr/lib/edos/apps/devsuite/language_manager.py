import json
import subprocess

class LanguageManager:
    def __init__(self):
        self.languages = {
            "python3": {"version": "3.12", "installed": True},
            "node": {"version": "20.x", "installed": True},
            "gcc": {"version": "13.2", "installed": True},
            "java": {"version": "21", "installed": True},
            "rust": {"version": "1.75", "installed": False},
            "go": {"version": "1.22", "installed": False},
        }

    def check_installed(self, lang):
        try:
            result = subprocess.run([lang, "--version"],
                capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False

    def install_language(self, lang):
        if lang in self.languages:
            self.languages[lang]["installed"] = True
            return True
        return False

    def get_language_info(self, lang):
        return self.languages.get(lang)

    def list_installed(self):
        return [l for l, info in self.languages.items() if info["installed"]]
