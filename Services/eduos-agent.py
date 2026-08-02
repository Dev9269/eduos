#!/usr/bin/env python3
"""
EduOS Agent â€” runs on every student PC.
Connects to the EduOS admin server and executes commands.
Supports FreeBSD (rc.d) and Linux (systemd) deployments.
"""

import asyncio
import base64
import json
import logging
import os
import platform
import signal
import subprocess
import sys
from pathlib import Path

import websockets

log = logging.getLogger(__name__)

CONFIG_FILE = Path('/etc/eduos/agent.conf')
# Also check local config for development/testing
LOCAL_CONFIG = Path.home() / '.eduos' / 'agent.conf'

FALLBACK_SERVER = 'ws://eduos-server.local:8765'


def _log_file_path() -> str:
    """Return a writable log path â€” falls back if /var/log is unavailable."""
    candidates = [
        os.environ.get('EDUOS_AGENT_LOG', ''),
        '/var/log/eduos-agent.log',
        str(Path.home() / '.eduos-agent.log'),
    ]
    for path in candidates:
        if not path:
            continue
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'a'):
                pass
            return path
        except OSError:
            continue
    return 'eduos-agent.log'


def load_config():
    """Load config from env var, then system path, then local path."""
    # Environment variable takes highest priority
    env_server = os.environ.get('EDUOS_SERVER_URL')
    if env_server:
        return {'server_url': env_server,
                'token': os.environ.get('EDUOS_TOKEN', '')}

    # System config (production), then local config (dev/testing)
    for config_path in [CONFIG_FILE, LOCAL_CONFIG]:
        if config_path.exists():
            try:
                return json.loads(config_path.read_text())
            except Exception:
                continue

    # Default fallback â€” mDNS discovery, then standard hostname
    return {
        'server_url': discover_server_mdns(),
        'token': '',
    }


def discover_server_mdns() -> str:
    """Try to find EduOS server on local network via hostname."""
    import socket
    try:
        # Try standard hostname first
        ip = socket.gethostbyname('eduos-server.local')
        return f'ws://{ip}:8765'
    except socket.gaierror:
        pass
    try:
        # Try common local hostnames
        for hostname in ['eduos-server', 'eduos-admin', 'admin']:
            try:
                ip = socket.gethostbyname(hostname)
                return f'ws://{ip}:8765'
            except socket.gaierror:
                continue
    except Exception:
        pass
    return FALLBACK_SERVER


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [AGENT] %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler(_log_file_path()),
        logging.StreamHandler()
    ]
)


def _is_freebsd() -> bool:
    return platform.system() == 'FreeBSD'


def _is_linux() -> bool:
    return platform.system() == 'Linux'


def _send_desktop_notification(title: str, message: str) -> str:
    """Show a desktop notification. Tries notify-send, then kdialog,
    then a plain print fallback. Returns which method was used."""
    try:
        subprocess.run(
            ['notify-send', '--expire-time=10000', title, message],
            check=False
        )
        return 'notify-send'
    except FileNotFoundError:
        pass
    try:
        subprocess.run(
            ['kdialog', '--title', title, '--passivepopup', message, '10'],
            check=False
        )
        return 'kdialog'
    except FileNotFoundError:
        pass
    log.info(f"[desktop notification] {title}: {message}")
    return 'log'


async def handle_command(command: dict) -> dict:
    """Execute a command from the admin server"""
    cmd = command.get('action', '')
    log.info(f"Received command: {cmd}")

    if cmd == 'ping':
        return {
            'status': 'pong',
            'hostname': platform.node(),
            'platform': platform.system(),
            'eduos_version': '2.0-freebsd'
        }

    elif cmd == 'exam_mode_on':
        if _is_freebsd():
            # FreeBSD: use rc.d service
            result = subprocess.run(
                ['service', 'eduos_exam', 'start'],
                capture_output=True, text=True
            )
        else:
            # Linux fallback
            result = subprocess.run(
                ['systemctl', 'start', 'eduos-exam-lock'],
                capture_output=True, text=True
            )
        return {
            'status': 'exam_mode_activated',
            'output': result.stdout,
            'platform': platform.system()
        }

    elif cmd == 'exam_mode_off':
        if _is_freebsd():
            result = subprocess.run(
                ['service', 'eduos_exam', 'stop'],
                capture_output=True, text=True
            )
        else:
            result = subprocess.run(
                ['systemctl', 'stop', 'eduos-exam-lock'],
                capture_output=True, text=True
            )
        return {
            'status': 'exam_mode_deactivated',
            'platform': platform.system()
        }

    elif cmd == 'lock_screen':
        if _is_freebsd():
            # FreeBSD/KDE: use xscreensaver or xdg-screensaver
            subprocess.run(['xdg-screensaver', 'lock'], check=False)
        else:
            subprocess.run(['loginctl', 'lock-sessions'], check=False)
        return {'status': 'screen_locked'}

    elif cmd == 'restart':
        subprocess.run(['shutdown', '-r', 'now'], check=False)
        return {'status': 'restarting'}

    elif cmd == 'shutdown':
        subprocess.run(['shutdown', '-p', 'now'], check=False)
        return {'status': 'shutting_down'}

    elif cmd == 'notify':
        """Show a desktop notification.
        command: {"title": "...", "message": "..."}"""
        title = command.get('title', 'EduOS')
        message = command.get('message', '')
        method = _send_desktop_notification(title, message)
        return {'status': 'notification_sent', 'method': method}

    elif cmd == 'exam_warning':
        """Warn a student that their exam is about to start/end."""
        mins = command.get('minutes', 5)
        exam = command.get('exam', 'the exam')
        title = 'EduOS Exam Warning'
        message = (
            f"{exam} starts in {mins} minute{'s' if mins != 1 else ''}. "
            "Please be ready and do not leave this machine."
        )
        method = _send_desktop_notification(title, message)
        return {'status': 'exam_warning_sent', 'method': method}

    elif cmd == 'get_status':
        import psutil
        return {
            'status': 'ok',
            'hostname': platform.node(),
            'platform': platform.system(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'ram_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
        }

    elif cmd == 'usb_lock':
        if _is_freebsd():
            # FreeBSD: disable USB storage via devd rules
            subprocess.run([
                'sh', '-c',
                'echo \'nomatch "ugen[0-9]* at *"\' > /etc/devd/eduos-usblock.conf'
            ], check=False)
            subprocess.run(['service', 'devd', 'restart'], check=False)
        return {'status': 'usb_locked', 'platform': platform.system()}

    elif cmd == 'usb_unlock':
        if _is_freebsd():
            subprocess.run([
                'rm', '-f', '/etc/devd/eduos-usblock.conf'
            ], check=False)
            subprocess.run(['service', 'devd', 'restart'], check=False)
        return {'status': 'usb_unlocked'}

    elif cmd == 'submit_exam':
        """Forward student's exam answers to server"""
        import urllib.request
        import hashlib
        config = load_config()
        server_http = config['server_url'].replace('ws://', 'http://')
        token = config.get('token', '')

        answers = command.get('answers', {})
        answers_json = json.dumps(answers)
        checksum = hashlib.sha256(answers_json.encode()).hexdigest()

        payload = json.dumps({
            'exam_id': command.get('exam_id'),
            'student_id': command.get('student_id'),
            'hostname': platform.node(),
            'answers': answers,
            'checksum': checksum
        }).encode()

        req = urllib.request.Request(
            f"{server_http}/exam/submit",
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
            return {'status': 'submitted', 'server_response': result}
        except Exception as e:
            return {'status': 'submit_failed', 'error': str(e)}

    elif cmd == 'apply_update':
        """Apply files pushed from admin server.
        Existing files are backed up to /opt/eduos/.backups/<version>/
        so a failed update can be rolled back."""
        files = command.get('files', [])
        version = command.get('version', 'unknown')
        base_path = Path('/opt/eduos')
        applied = []
        errors = []

        backup_dir = base_path / '.backups' / version
        if files:
            backup_dir.mkdir(parents=True, exist_ok=True)
            manifest = []

        for file_entry in files:
            try:
                rel_path = file_entry['path']
                content = base64.b64decode(file_entry['content_b64'])
                target = base_path / rel_path

                # Back up the previous version of the file (if any)
                if target.exists():
                    backup_file = backup_dir / rel_path
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    backup_file.write_bytes(target.read_bytes())
                    manifest.append(rel_path)
                    log.info(f"Backed up {rel_path} -> {backup_file}")

                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
                applied.append(rel_path)
                log.info(f"Update applied: {rel_path}")
            except Exception as e:
                errors.append(f"{file_entry.get('path','?')}: {e}")
                log.error(f"Update failed for {file_entry.get('path')}: {e}")

        if files:
            # Write a manifest so rollback knows exactly what to restore
            manifest_path = backup_dir / 'manifest.json'
            manifest_path.write_text(json.dumps({
                'version': version,
                'applied': applied,
                'files': [f['path'] for f in files],
            }, indent=2))

        result = {
            'status': 'update_applied',
            'version': version,
            'applied': applied,
            'errors': errors
        }

        if command.get('restart_agent'):
            log.info("Restarting agent after update...")
            import threading
            def restart():
                import time
                time.sleep(2)
                os.execv(sys.executable, [sys.executable] + sys.argv)
            threading.Thread(target=restart, daemon=True).start()

        return result

    elif cmd == 'rollback':
        """Restore files from the most recent update backup.
        command: {"version": "1.2.3"} or omitted for latest backup."""
        base_path = Path('/opt/eduos')
        backup_root = base_path / '.backups'

        version = command.get('version')
        if not version:
            if not backup_root.exists():
                return {'status': 'rollback_failed',
                        'error': 'no backups found'}
            versions = sorted(
                [p for p in backup_root.iterdir() if p.is_dir()],
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            if not versions:
                return {'status': 'rollback_failed',
                        'error': 'no backups found'}
            version = versions[0].name

        backup_dir = backup_root / version
        if not backup_dir.is_dir():
            return {'status': 'rollback_failed',
                    'error': f'no backup for version {version}'}

        manifest_path = backup_dir / 'manifest.json'
        files_to_restore = []
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text())
                files_to_restore = manifest.get('files', [])
            except (json.JSONDecodeError, OSError):
                files_to_restore = []

        restored = []
        removed = []
        errors = []

        # Restore from backup copies
        if files_to_restore:
            for rel_path in files_to_restore:
                backup_file = backup_dir / rel_path
                target = base_path / rel_path
                try:
                    if backup_file.exists():
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(backup_file.read_bytes())
                        restored.append(rel_path)
                        log.info(f"Rolled back {rel_path} from v{version}")
                    else:
                        # File was new in the update - remove it
                        if target.exists():
                            target.unlink()
                            removed.append(rel_path)
                except Exception as e:
                    errors.append(f"{rel_path}: {e}")
        else:
            # No manifest - restore every backup file we have
            for backup_file in backup_dir.rglob('*'):
                if not backup_file.is_file() or backup_file.name == 'manifest.json':
                    continue
                rel_path = backup_file.relative_to(backup_dir)
                target = base_path / rel_path
                try:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(backup_file.read_bytes())
                    restored.append(str(rel_path))
                except Exception as e:
                    errors.append(f"{rel_path}: {e}")

        log.info(f"Rollback to v{version} complete: "
                 f"{len(restored)} restored, {len(removed)} removed")
        return {
            'status': 'rolled_back',
            'version': version,
            'restored': restored,
            'removed': removed,
            'errors': errors
        }

    return {'status': 'unknown_command', 'cmd': cmd}


async def health_reporter(ws):
    """Report CPU/RAM/disk health to the server every 60 seconds."""
    try:
        import psutil
    except ImportError:
        log.warning("psutil unavailable — health reporting disabled")
        return
    while True:
        try:
            await ws.send(json.dumps({
                'type': 'health_report',
                'hostname': platform.node(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'ram_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
            }))
        except Exception as e:
            log.warning(f"Health report failed: {e}")
            return
        await asyncio.sleep(60)


async def agent_loop():
    config = load_config()
    server_url = config['server_url']
    token = config.get('token', '')

    while True:
        try:
            log.info(f"Connecting to server: {server_url}")
            async with websockets.connect(
                server_url,
                extra_headers={'Authorization': f'Bearer {token}'},
                ping_interval=30,
                ping_timeout=10,
            ) as ws:
                log.info("Connected to EduOS server")

                # Register this machine
                await ws.send(json.dumps({
                    'type': 'register',
                    'hostname': platform.node(),
                    'mac': get_mac_address(),
                }))

                # Health reporting task
                reporter = asyncio.create_task(health_reporter(ws))

                # Listen for commands
                async for message in ws:
                    try:
                        command = json.loads(message)
                        result = await handle_command(command)
                        await ws.send(json.dumps(result))
                    except Exception as e:
                        log.error(f"Command error: {e}")
                        await ws.send(json.dumps({'status': 'error',
                                                  'message': str(e)}))

                reporter.cancel()

        except Exception as e:
            log.warning(f"Connection lost: {e}. Retrying in 10s...")
            await asyncio.sleep(10)


def get_mac_address():
    try:
        import uuid
        return ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff)
                        for i in range(0, 48, 8)][::-1])
    except Exception:
        return 'unknown'


if __name__ == '__main__':
    # Block termination signals â€” agent must not be killable by student
    signal.signal(signal.SIGTERM, lambda s, f: log.warning("SIGTERM blocked"))
    signal.signal(signal.SIGHUP, lambda s, f: log.warning("SIGHUP blocked"))
    asyncio.run(agent_loop())
