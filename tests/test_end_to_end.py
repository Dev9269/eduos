"""EduOS End-to-End Integration Tests"""
import json, os, sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
import jwt

os.environ['EDUOS_DB_PATH'] = '/tmp/eduos_e2e_test.db'
Path('/tmp/eduos_e2e_test.db').unlink(missing_ok=True)

def setup_client():
    from Server.eduos_server import app, init_db
    init_db()
    return TestClient(app)

def make_token():
    from Server.eduos_server import load_or_generate_secret
    secret = load_or_generate_secret()
    return jwt.encode(
        {'role': 'admin',
         'exp': datetime.now(timezone.utc) + timedelta(hours=1)},
        secret, algorithm='HS256'
    )

@pytest.fixture(scope='module')
def client(): return setup_client()

@pytest.fixture(scope='module')
def h(): return {'Authorization': f'Bearer {make_token()}'}

@pytest.fixture(scope='module', autouse=True)
def cleanup_roster(client, h):
    """Remove E2E students from the shared roster after the module runs,
    so later test modules (test_exam_flow) see a clean roster."""
    yield
    for sid in ['E001', 'E002', 'E003']:
        client.delete(f'/roster/{sid}', headers=h)

def test_e2e_01_health(client, h):
    assert client.get('/health').json()['status'] == 'ok'

def test_e2e_02_roster_bulk(client, h):
    students = [
        {'student_id':'E001','name':'Arjun Mehta','roll_number':'22CS001','department':'CSE','semester':'5'},
        {'student_id':'E002','name':'Priya Shah','roll_number':'22CS002','department':'CSE','semester':'5'},
        {'student_id':'E003','name':'Raj Patel','roll_number':'22CS003','department':'CSE','semester':'5'},
    ]
    r = client.post('/roster/bulk', json={'students': students}, headers=h)
    assert r.status_code == 200 and r.json()['added'] == 3

def test_e2e_03_validate_student(client, h):
    assert client.get('/roster/validate/E001', headers=h).json()['name'] == 'Arjun Mehta'
    assert client.get('/roster/validate/FAKE999', headers=h).status_code == 404

def test_e2e_04_push_exam(client, h):
    r = client.post('/exam/push', json={
        'name': 'Python Mid Sem', 'exam_id': 42,
        'questions': [
            {'id':'q1','type':'mcq','text':'What is Python?','options':['A','B','C','D']},
            {'id':'q2','type':'code','text':'Write add function'}
        ]
    }, headers=h)
    assert r.status_code == 200

def test_e2e_05_submissions(client, h):
    for sub in [
        {'exam_id':42,'student_id':'E001','hostname':'PC-01',
         'answers':{'q1':'A','q2':'def add(a,b): return a+b'}},
        {'exam_id':42,'student_id':'E002','hostname':'PC-02',
         'answers':{'q1':'A','q2':'def add(a,b): return a+b'}},
        {'exam_id':42,'student_id':'E003','hostname':'PC-03',
         'answers':{'q1':'B','q2':'def add(x,y):\n    return x+y'}},
    ]:
        r = client.post('/exam/submit', json=sub, headers=h)
        assert r.status_code == 200 and r.json()['status'] == 'received'

def test_e2e_06_view_submissions(client, h):
    r = client.get('/exam/submissions/42', headers=h)
    assert r.json()['total'] == 3

def test_e2e_07_similarity_flags_cheating(client, h):
    r = client.get('/exam/submissions/42/similarity', headers=h)
    data = r.json()
    assert data['suspicious_pairs'] >= 1
    pair = data['results'][0]
    assert {'E001','E002'} == {pair['student_a'], pair['student_b']}
    assert pair['similarity'] >= 0.9

def test_e2e_08_export(client, h):
    r = client.get('/exam/submissions/42/export', headers=h)
    assert len(r.json()['submissions']) == 3
    assert 'answers' in r.json()['submissions'][0]

def test_e2e_09_schedule_exam(client, h):
    future = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S')
    r = client.post('/exam/schedule', json={
        'exam_id':99,'exam_name':'Final','activate_at':future,
        'duration_minutes':90,'exam_config':{}
    }, headers=h)
    assert r.json()['status'] == 'scheduled'
    assert r.json()['seconds_until_activation'] > 0

def test_e2e_10_cancel_schedule(client, h):
    r = client.delete('/exam/schedule/99', headers=h)
    assert r.json()['status'] == 'cancelled'
