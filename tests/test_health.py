"""
EduOS Health Monitoring Tests
Covers /health/report, /health/metrics/{hostname}, /health/alerts,
and auto-resolution of alerts when metrics drop back under threshold.
"""
import sys, json, os
from pathlib import Path
from datetime import datetime, timedelta, timezone
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
import jwt

os.environ['EDUOS_DB_PATH'] = '/tmp/eduos_health_test.db'
Path('/tmp/eduos_health_test.db').unlink(missing_ok=True)


def get_client():
    from Server.eduos_server import app, init_db
    init_db()
    return TestClient(app)


def make_token(role='admin'):
    from Server.eduos_server import load_or_generate_secret
    s = load_or_generate_secret()
    return jwt.encode({'role': role,
                       'exp': datetime.now(timezone.utc) + timedelta(hours=1)},
                      s, algorithm='HS256')


@pytest.fixture(scope='module', autouse=True)
def reset_health_state():
    from Server.eduos_server import active_alerts, record_health_report
    active_alerts.clear()
    yield
    active_alerts.clear()


def test_health_report_requires_auth():
    """Unauthenticated health reports must be rejected"""
    client = get_client()
    r = client.post("/health/report", json={
        'hostname': 'lab1', 'cpu_percent': 50,
        'ram_percent': 50, 'disk_percent': 50
    })
    assert r.status_code in [401, 403, 422]


def test_health_report_recorded():
    """Valid report stores metrics and confirms no alert"""
    client = get_client()
    token = make_token()
    r = client.post("/health/report", json={
        'hostname': 'lab1', 'cpu_percent': 30.0,
        'ram_percent': 40.0, 'disk_percent': 50.0
    }, headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200
    body = r.json()
    assert body['status'] == 'recorded'
    assert body['alert'] is False


def test_health_report_missing_hostname_rejected():
    client = get_client()
    token = make_token()
    r = client.post("/health/report", json={
        'cpu_percent': 30.0, 'ram_percent': 40.0, 'disk_percent': 50.0
    }, headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 400


def test_health_metrics_returns_history():
    """/health/metrics/{hostname} returns recent reports in order"""
    client = get_client()
    token = make_token()
    for i in range(3):
        client.post("/health/report", json={
            'hostname': 'lab2', 'cpu_percent': 10.0 + i,
            'ram_percent': 20.0, 'disk_percent': 30.0
        }, headers={'Authorization': f'Bearer {token}'})
    r = client.get("/health/metrics/lab2",
                   headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200
    body = r.json()
    assert body['hostname'] == 'lab2'
    assert len(body['metrics']) == 3
    assert body['metrics'][0]['cpu_percent'] == 12.0


def test_high_cpu_raises_alert():
    """CPU above 80% must create an alert"""
    client = get_client()
    token = make_token()
    r = client.post("/health/report", json={
        'hostname': 'lab3', 'cpu_percent': 95.0,
        'ram_percent': 30.0, 'disk_percent': 40.0
    }, headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200
    assert r.json()['alert'] is True

    alerts = client.get("/health/alerts",
                        headers={'Authorization': f'Bearer {token}'}).json()
    assert alerts['count'] == 1
    assert alerts['alerts'][0]['hostname'] == 'lab3'
    assert alerts['alerts'][0]['metric'] == 'cpu'


def test_high_disk_raises_alert():
    client = get_client()
    token = make_token()
    r = client.post("/health/report", json={
        'hostname': 'lab4', 'cpu_percent': 20.0,
        'ram_percent': 20.0, 'disk_percent': 96.0
    }, headers={'Authorization': f'Bearer {token}'})
    assert r.json()['alert'] is True

    alerts = client.get("/health/alerts",
                        headers={'Authorization': f'Bearer {token}'}).json()
    hosts = {a['hostname']: a for a in alerts['alerts']}
    assert hosts['lab4']['metric'] == 'disk'


def test_alert_auto_resolves():
    """Metrics dropping back under threshold clears the alert"""
    client = get_client()
    token = make_token()
    client.post("/health/report", json={
        'hostname': 'lab5', 'cpu_percent': 90.0,
        'ram_percent': 30.0, 'disk_percent': 30.0
    }, headers={'Authorization': f'Bearer {token}'})
    assert client.get("/health/alerts",
                      headers={'Authorization': f'Bearer {token}'}).json()['count'] >= 1

    client.post("/health/report", json={
        'hostname': 'lab5', 'cpu_percent': 20.0,
        'ram_percent': 30.0, 'disk_percent': 30.0
    }, headers={'Authorization': f'Bearer {token}'})
    alerts = client.get("/health/alerts",
                        headers={'Authorization': f'Bearer {token}'}).json()
    hosts = [a['hostname'] for a in alerts['alerts']]
    assert 'lab5' not in hosts
