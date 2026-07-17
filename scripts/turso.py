#!/usr/bin/env python3
"""Query Turso database from terminal.

Usage:
    python3 scripts/turso.py "SELECT * FROM users"
    python3 scripts/turso.py "SELECT name FROM sqlite_master WHERE type='table'"
"""
import json
import os
import sys
import re
import requests

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(DIR, ".env")

env = {}
with open(ENV_PATH) as f:
    for line in f:
        m = re.match(r"^\s*(\w+)\s*=\s*(.+?)\s*$", line)
        if m:
            env[m.group(1)] = m.group(2)

turso_url = env.get("TURSO_URL", "")
turso_token = env.get("TURSO_TOKEN", "")
url = turso_url.replace("libsql://", "https://") + "/v2/pipeline"

sql = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"

payload = {"requests": [{"type": "execute", "stmt": {"sql": sql}}]}
resp = requests.post(url, json=payload, headers={
    "Authorization": f"Bearer {turso_token}",
    "Content-Type": "application/json",
}, timeout=10)

data = resp.json()
res = data["results"][0]
if res["type"] == "error":
    print("ERROR:", res["error"]["message"])
    sys.exit(1)

result = res["response"]["result"]
cols = [c["name"] for c in result["cols"]]
print(" | ".join(cols))
print("-" * 50)
for row in result["rows"]:
    print(" | ".join(str(c.get("value", "")) for c in row))
