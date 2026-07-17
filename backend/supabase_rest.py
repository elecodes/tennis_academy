import os
import requests
from dotenv import load_dotenv

load_dotenv()

_SUPABASE_URL = os.environ.get("SUPABASE_URL")
_SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
_ACADEMY_AVAILABLE = bool(_SUPABASE_URL and _SUPABASE_SERVICE_KEY)


def is_rest_available():
    return _ACADEMY_AVAILABLE


def _headers():
    return {
        "apikey": _SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {_SUPABASE_SERVICE_KEY}",
        "Accept": "application/json",
    }


def get_table(table, order=None, select="*"):
    if not is_rest_available():
        return None
    url = _SUPABASE_URL.rstrip("/")
    params = {"select": select}
    if order:
        params["order"] = order
    try:
        resp = requests.get(f"{url}/{table}", headers=_headers(), params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return None
