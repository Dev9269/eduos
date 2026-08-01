#!/usr/bin/env python3
"""
Generate an admin JWT token for EduOS Server authentication.
Run this on the admin laptop after starting the server.
Usage: python3 Server/generate-admin-token.py
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import jwt
except ImportError:
    os.system("pip3 install pyjwt --break-system-packages -q")
    import jwt

from Server.eduos_server import load_or_generate_secret
from datetime import datetime, timedelta, timezone

secret = load_or_generate_secret()
now = datetime.now(timezone.utc)
payload = {
    'role': 'admin',
    'issued': now.isoformat(),
    'exp': now + timedelta(days=365)
}

token = jwt.encode(payload, secret, algorithm='HS256')
print("\n=== EduOS Admin Token ===")
print(f"\n{token}\n")
print("Copy this token into the Admin Panel settings.")
print("Keep it secret — it grants full control of all machines.\n")
