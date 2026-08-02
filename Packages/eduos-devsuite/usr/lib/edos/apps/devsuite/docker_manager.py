"""
EduOS DevSuite Container Manager
Supports: Podman (FreeBSD/Linux) and Docker (Linux)
"""
import json
import subprocess
import shutil


def _get_runtime() -> str:
    """Auto-detect container runtime"""
    for r in ['podman', 'docker']:
        if shutil.which(r):
            return r
    return None


class DockerManager:
    def __init__(self):
        self.containers = {}
        self.runtime = _get_runtime()

    def _run(self, *args, timeout=30, capture=True):
        if not self.runtime:
            raise RuntimeError(
                "No container runtime found.\n"
                "FreeBSD: pkg install podman\n"
                "Linux: apt-get install docker.io"
            )
        cmd = [self.runtime] + list(args)
        result = subprocess.run(cmd, capture_output=capture, text=True, timeout=timeout)
        return result

    def list_containers(self):
        try:
            result = self._run("ps", "-a", "--format", "json")
            containers = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    try:
                        containers.append(json.loads(line))
                    except Exception:
                        pass
            return containers
        except Exception:
            return []

    def start_container(self, container_id):
        try:
            self._run("start", container_id)
            return True
        except Exception:
            return False

    def stop_container(self, container_id):
        try:
            self._run("stop", container_id, timeout=30)
            return True
        except Exception:
            return False

    def build_image(self, dockerfile_path, tag):
        try:
            self._run("build", "-t", tag, dockerfile_path, timeout=300)
            return True
        except Exception:
            return False

    def get_stats(self):
        containers = self.list_containers()
        return {
            "runtime": self.runtime or "not installed",
            "containers": len(containers),
            "disk_usage": "calculating..."
        }

    def is_available(self) -> bool:
        return self.runtime is not None
