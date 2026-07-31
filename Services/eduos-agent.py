#!/usr/bin/env python3
"""
EduOS Agent — runs on every student PC as a systemd service.
Connects to the admin server and executes commands.
"""

import asyncio
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
DEFAULT_SERVER = 'ws://192.168.1.10:8765'


def _log_file_path() -> str:
    """Return a writable log path — falls back if /var/log is unavailable."""
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
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {'server_url': DEFAULT_SERVER, 'token': ''}


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [AGENT] %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler(_log_file_path()),
        logging.StreamHandler()
    ]
)


async def handle_command(command: dict) -> dict:
    """Execute a command from the admin server"""
    cmd = command.get('action', '')
    log.info(f"Received command: {cmd}")

    if cmd == 'ping':
        return {'status': 'pong', 'hostname': platform.node()}

    elif cmd == 'exam_mode_on':
        subprocess.run(['systemctl', 'start', 'eduos-exam-lock'],
                       check=False)
        return {'status': 'exam_mode_activated'}

    elif cmd == 'exam_mode_off':
        subprocess.run(['systemctl', 'stop', 'eduos-exam-lock'],
                       check=False)
        return {'status': 'exam_mode_deactivated'}

    elif cmd == 'lock_screen':
        subprocess.run(['loginctl', 'lock-sessions'], check=False)
        return {'status': 'screen_locked'}

    elif cmd == 'restart':
        subprocess.run(['shutdown', '-r', 'now'], check=False)
        return {'status': 'restarting'}

    elif cmd == 'shutdown':
        subprocess.run(['shutdown', '-h', 'now'], check=False)
        return {'status': 'shutting_down'}

    elif cmd == 'get_status':
        import psutil
        return {
            'status': 'ok',
            'hostname': platform.node(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'ram_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
        }

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
    # Block termination signals — agent must not be killable by student
    signal.signal(signal.SIGTERM, lambda s, f: log.warning("SIGTERM blocked"))
    signal.signal(signal.SIGHUP, lambda s, f: log.warning("SIGHUP blocked"))
    asyncio.run(agent_loop())
