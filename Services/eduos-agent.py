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
        """Apply files pushed from admin server"""
        files = command.get('files', [])
        version = command.get('version', 'unknown')
        base_path = Path('/opt/eduos')
        applied = []
        errors = []

        for file_entry in files:
            try:
                rel_path = file_entry['path']
                content = base64.b64decode(file_entry['content_b64'])
                target = base_path / rel_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
                applied.append(rel_path)
                log.info(f"Update applied: {rel_path}")
            except Exception as e:
                errors.append(f"{file_entry.get('path','?')}: {e}")
                log.error(f"Update failed for {file_entry.get('path')}: {e}")

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

    return {'status': 'unknown_command', 'cmd': cmd}


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
