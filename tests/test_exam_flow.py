"""
Integration test for EduOS exam submission flow.
Tests: push exam → agent receives → student submits → admin retrieves
"""
import json
import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta, timezone


def make_token():
    from Server.eduos_server import load_or_generate_secret
    secret = load_or_generate_secret()
    return jwt.encode(
        {'role': 'admin', 'exp': datetime.now(timezone.utc) + timedelta(hours=1)},
        secret, algorithm='HS256'
    )


def get_client():
    from Server.eduos_server import app, init_db
    os.environ['EDUOS_DB_PATH'] = str(
        Path(tempfile.mkdtemp()) / 'test_exam_flow.db'
    )
    init_db()
    return TestClient(app)


def test_submit_exam():
    client = get_client()
    token = make_token()
    headers = {'Authorization': f'Bearer {token}'}

    resp = client.post("/exam/submit", json={
        'exam_id': 1,
        'student_id': 'student_001',
        'hostname': 'PC-TEST-01',
        'answers': {'q1': 'A', 'q2': 'B', 'q3': 'C'}
    }, headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'received'
    assert 'checksum' in data
    assert len(data['checksum']) == 64  # SHA256 hex


def test_get_submissions():
    client = get_client()
    token = make_token()
    headers = {'Authorization': f'Bearer {token}'}

    # Submit first
    client.post("/exam/submit", json={
        'exam_id': 99,
        'student_id': 'student_002',
        'hostname': 'PC-02',
        'answers': {'q1': 'D'}
    }, headers=headers)

    # Retrieve
    resp = client.get("/exam/submissions/99", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data['total'] >= 1
    assert data['submissions'][0]['student_id'] == 'student_002'


def test_submit_missing_fields():
    client = get_client()
    token = make_token()
    headers = {'Authorization': f'Bearer {token}'}

    resp = client.post("/exam/submit", json={
        'exam_id': 1
        # missing student_id and answers
    }, headers=headers)
    assert resp.status_code == 400


def test_unauthenticated_submit():
    client = get_client()
    resp = client.post("/exam/submit", json={
        'exam_id': 1,
        'student_id': 'hacker',
        'answers': {}
    })
    assert resp.status_code in [401, 403]
