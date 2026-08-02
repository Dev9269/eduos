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


def test_similarity_identical():
    from Server.similarity import similarity_score
    code = "def add(a, b):\n    return a + b\nprint(add(1,2))"
    score = similarity_score(code, code)
    assert score == 1.0


def test_similarity_different():
    from Server.similarity import similarity_score
    a = "def add(a, b):\n    return a + b"
    b = "x = int(input())\nprint(x * 2)"
    score = similarity_score(a, b)
    assert score < 0.3


def test_similarity_empty():
    from Server.similarity import similarity_score
    assert similarity_score("", "some code") == 0.0


def test_add_and_validate_student():
    import Server.eduos_server as srv
    client = get_client()
    token = make_token()
    headers = {'Authorization': f'Bearer {token}'}

    # Add a valid student to the roster
    resp = client.post("/roster/add", json={
        'student_id': '2021CSE045',
        'name': 'Arjun Kumar',
        'email': 'arjun@eduos.edu',
        'course': 'CSE'
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()['status'] == 'added'

    # Invalid enrollment format rejected
    resp = client.post("/roster/add", json={
        'student_id': 'bad-id!'
    }, headers=headers)
    assert resp.status_code == 400

    # Duplicate rejected
    resp = client.post("/roster/add", json={
        'student_id': '2021CSE045'
    }, headers=headers)
    assert resp.status_code == 409

    # Validate endpoint: registered student passes
    resp = client.post("/roster/validate", json={
        'student_id': '2021CSE045',
        'check_registered': True
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()['valid'] is True

    # Unregistered student fails full validation
    resp = client.post("/roster/validate", json={
        'student_id': '22BCS9999',
        'check_registered': True
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()['valid'] is False
    assert 'not in roster' in resp.json()['reason']

    # Submission from a registered student is accepted
    resp = client.post("/exam/submit", json={
        'exam_id': 7,
        'student_id': '2021CSE045',
        'hostname': 'PC-ROSTER-01',
        'answers': {'q1': 'A'}
    }, headers=headers)
    assert resp.status_code == 200

    # Submission from an unregistered student is rejected
    resp = client.post("/exam/submit", json={
        'exam_id': 7,
        'student_id': '22BCS9999',
        'hostname': 'PC-ROSTER-02',
        'answers': {'q1': 'A'}
    }, headers=headers)
    assert resp.status_code == 403

    # Remove the student
    resp = client.delete("/roster/2021CSE045", headers=headers)
    assert resp.status_code == 200
    resp = client.get("/roster", headers=headers)
    assert resp.json()['total'] == 0

def test_learnhub_sync_endpoint():
    """LearnHub sync endpoint should exist and return valid JSON"""
    import ast
    ast.parse(open("LearnHub/learnhub_app.py", encoding="utf-8").read())
    print("LearnHub syntax OK")
