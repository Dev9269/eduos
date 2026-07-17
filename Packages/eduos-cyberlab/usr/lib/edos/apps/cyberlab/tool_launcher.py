import subprocess
import shlex

class ToolLauncher:
    def __init__(self):
        self.tools = {
            "nmap": {"command": "nmap", "available": False},
            "wireshark": {"command": "wireshark", "available": False},
            "netstat": {"command": "netstat", "available": False},
            "tcpdump": {"command": "tcpdump", "available": False},
        }
        self._check_available()

    def _check_available(self):
        for name, info in self.tools.items():
            try:
                subprocess.run(["which", info["command"]],
                    capture_output=True, timeout=5)
                self.tools[name]["available"] = True
            except Exception:
                pass

    def run_tool(self, tool_name, args=""):
        info = self.tools.get(tool_name)
        if not info or not info["available"]:
            return {"error": f"Tool {tool_name} not available"}

        try:
            cmd = f"{info['command']} {args}"
            result = subprocess.run(
                shlex.split(cmd), capture_output=True,
                text=True, timeout=60
            )
            return {"stdout": result.stdout, "stderr": result.stderr,
                    "return_code": result.returncode}
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except Exception as e:
            return {"error": str(e)}

    def list_available(self):
        return [name for name, info in self.tools.items() if info["available"]]
