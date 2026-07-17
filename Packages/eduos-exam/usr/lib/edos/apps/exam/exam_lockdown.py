import subprocess
import sys
import platform


class ExamLockdown:
    def __init__(self):
        self.active = False
        self.system = platform.system()

    def activate(self):
        self.active = True
        return True

    def deactivate(self):
        self.active = False
        return True

    def check_environment(self):
        return {
            "no_browser": self._check_no_browser(),
            "no_terminal": self._check_no_terminal(),
            "no_devtools": self._check_no_devtools(),
            "locked_down": self.active,
        }

    def _check_no_browser(self):
        browsers = [
            "firefox",
            "chrome",
            "chromium",
            "brave",
            "opera",
            "msedge",
            "safari",
        ]
        return not self._find_processes(browsers)

    def _check_no_terminal(self):
        terminals = [
            "konsole",
            "gnome-terminal",
            "xterm",
            "alacritty",
            "kitty",
            "tmux",
            "screen",
        ]
        return not self._find_processes(terminals)

    def _check_no_devtools(self):
        tools = [
            "code",
            "code-oss",
            "atom",
            "sublime_text",
            "notepad++",
            "gdb",
            "strace",
        ]
        return not self._find_processes(tools)

    def _find_processes(self, names):
        if self.system == "Windows":
            try:
                result = subprocess.run(
                    ["tasklist", "/FO", "CSV", "/NH"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                running = result.stdout.lower()
                return any(name.lower() in running for name in names)
            except Exception:
                return False
        else:
            try:
                for name in names:
                    result = subprocess.run(
                        ["pgrep", "-x", name], capture_output=True, timeout=5
                    )
                    if result.returncode == 0:
                        return True
                return False
            except Exception:
                return False
