import os
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, '.')


def test_server_starts():
    # Point the DB at a temp path so tests never touch /var/lib
    os.environ['EDUOS_DB_PATH'] = str(
        Path(tempfile.mkdtemp()) / 'test_server.db'
    )
    from fastapi.testclient import TestClient
    from Server.eduos_server import app, init_db
    init_db()
    client = TestClient(app)
    # Unauthenticated request should return 401/403
    r = client.get("/devices")
    assert r.status_code in [401, 403]


def test_health_endpoint():
    os.environ['EDUOS_DB_PATH'] = str(
        Path(tempfile.mkdtemp()) / 'test_server.db'
    )
    from fastapi.testclient import TestClient
    from Server.eduos_server import app, init_db
    init_db()
    client = TestClient(app)
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert 'EduOS Server' in r.json().get('info', {}).get('title', '')


def _load_package_server():
    """Load Packages/eduos-server api_server via importlib (dir has hyphens)."""
    import importlib.util
    pkg_dir = Path('Packages/eduos-server/usr/lib/edos/server')
    sys.path.insert(0, str(pkg_dir))
    spec = importlib.util.spec_from_file_location(
        "api_server", pkg_dir / "api_server.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_users_endpoint_requires_auth():
    from fastapi.testclient import TestClient
    api_server = _load_package_server()
    os.environ['EDUOS_DB_PATH'] = str(
        Path(tempfile.mkdtemp()) / 'pkg_test.db'
    )
    with TestClient(api_server.app) as client:
        r = client.get("/api/users")
        assert r.status_code in [401, 403], f"Expected auth error, got {r.status_code}"


def test_courses_endpoint_requires_admin():
    from fastapi.testclient import TestClient
    api_server = _load_package_server()
    os.environ['EDUOS_DB_PATH'] = str(
        Path(tempfile.mkdtemp()) / 'pkg_test.db'
    )
    with TestClient(api_server.app) as client:
        r = client.post("/api/courses", json={"name": "test", "description": ""})
        assert r.status_code in [401, 403]


def test_submissions_endpoint_requires_auth():
    from fastapi.testclient import TestClient
    api_server = _load_package_server()
    os.environ['EDUOS_DB_PATH'] = str(
        Path(tempfile.mkdtemp()) / 'pkg_test.db'
    )
    with TestClient(api_server.app) as client:
        r = client.get("/api/submissions")
        assert r.status_code in [401, 403]


def test_student_cannot_access_admin_endpoints():
    """Student token on /api/users must be 403 (admin only)."""
    import jwt as pyjwt
    from datetime import datetime, timedelta
    from fastapi.testclient import TestClient
    api_server = _load_package_server()
    os.environ['EDUOS_DB_PATH'] = str(
        Path(tempfile.mkdtemp()) / 'pkg_test.db'
    )
    token = pyjwt.encode(
        {'sub': '2', 'username': 'stu', 'role': 'student',
         'exp': datetime.utcnow() + timedelta(hours=1)},
        api_server.SECRET_KEY, algorithm='HS256'
    )
    with TestClient(api_server.app) as client:
        r = client.get("/api/users", headers={'Authorization': f'Bearer {token}'})
        assert r.status_code == 403


def test_admin_can_list_users_after_login():
    from fastapi.testclient import TestClient
    api_server = _load_package_server()
    os.environ['EDUOS_DB_PATH'] = str(
        Path(tempfile.mkdtemp()) / 'pkg_test.db'
    )
    with TestClient(api_server.app) as client:
        r = client.post("/api/auth/login", json={
            'username': 'admin', 'password': 'EduOS@Admin2025!'
        })
        assert r.status_code == 200
        token = r.json()['access_token']
        r = client.get("/api/users", headers={'Authorization': f'Bearer {token}'})
        assert r.status_code == 200
        assert r.json()['total'] >= 1
