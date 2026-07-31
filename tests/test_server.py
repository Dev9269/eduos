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
