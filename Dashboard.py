# dashboard.py
import json

def serialize_user(u):
    return json.dumps(u, indent=2)
