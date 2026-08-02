"""
EduOS Daemon Correctness Tests
Static-analysis (AST) checks over the four service daemons:
- No hardcoded external URLs (edos.edu etc.)
- Config is loaded from file (load_config), never hardcoded
- Retry/backoff pattern present (except ... sleep)
- Main entry point guarded by __main__
"""
import ast
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

DAEMON_DIR = Path('Packages/eduos-services/usr/lib/edos/services')
DAEMONS = [
    'exam-daemon.py',
    'sync-daemon.py',
    'security-daemon.py',
    'update-daemon.py',
]

EXTERNAL_URL_MARKERS = [
    'edos.edu',
    'https://exam',
    'https://sync',
    'https://update',
    'https://security',
]


@pytest.fixture(scope='module')
def daemon_sources():
    sources = {}
    for name in DAEMONS:
        path = DAEMON_DIR / name
        assert path.exists(), f"missing daemon: {path}"
        sources[name] = path.read_text(encoding='utf-8')
    return sources


@pytest.mark.parametrize('name', DAEMONS)
def test_daemon_exists(name):
    assert (DAEMON_DIR / name).exists()


@pytest.mark.parametrize('name', DAEMONS)
def test_daemon_no_hardcoded_external_urls(daemon_sources, name):
    """Daemons must not contain hardcoded external server URLs."""
    src = daemon_sources[name]
    for marker in EXTERNAL_URL_MARKERS:
        assert marker not in src, f"{name} still references {marker}"


@pytest.mark.parametrize('name', DAEMONS)
def test_daemon_loads_config_from_file(daemon_sources, name):
    """Daemon must define/use a load_config() that reads agent.conf."""
    src = daemon_sources[name]
    assert 'def load_config' in src, f"{name} missing load_config()"
    assert 'agent.conf' in src, f"{name} does not read agent.conf"
    assert 'server_url' in src, f"{name} does not use server_url"


@pytest.mark.parametrize('name', DAEMONS)
def test_daemon_has_retry_with_backoff(daemon_sources, name):
    """Daemon must retry after a delay when the server is unreachable."""
    src = daemon_sources[name]
    assert 'except' in src
    assert 'sleep' in src, f"{name} has no retry sleep"
    # Backoff must be bounded (min(...) with a cap)
    assert 'min(' in src, f"{name} lacks bounded backoff"


@pytest.mark.parametrize('name', DAEMONS)
def test_daemon_parses_as_valid_python(daemon_sources, name):
    ast.parse(daemon_sources[name])


@pytest.mark.parametrize('name', DAEMONS)
def test_daemon_has_main_guard(daemon_sources, name):
    assert '__main__' in daemon_sources[name], f"{name} missing __main__ guard"
