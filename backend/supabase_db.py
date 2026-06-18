import os
import requests

SUPABASE_URL = os.environ.get(
    "SUPABASE_URL",
    "https://ypbwlpeighgpafocauzp.supabase.co/rest/v1",
)
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_ANON_KEY")


def _client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return {
        "url": SUPABASE_URL.rstrip("/"),
        "headers": {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Accept": "application/json",
        },
    }


def _fetch(table, order=None):
    client = _client()
    if not client:
        return None
    params = {}
    if order:
        params["order"] = order
    resp = requests.get(
        f"{client['url']}/{table}",
        headers=client["headers"],
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def fetch_students():
    return _fetch("students", order="name.asc")


def fetch_coaches():
    return _fetch("coaches", order="name.asc")


def fetch_lessons():
    return _fetch("lessons", order="day.asc,time.asc")
