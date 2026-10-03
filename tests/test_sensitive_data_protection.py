import os
import pytest
from backend.app import app

def test_session_cookie_security_config():
    """Verify session cookie security settings (HttpOnly and SameSite)."""
    assert app.config.get("SESSION_COOKIE_HTTPONLY") is True
    assert app.config.get("SESSION_COOKIE_SAMESITE") in ("Lax", "Strict")


def test_no_hardcoded_smtp_password_in_app():
    """Verify SENDER_PASSWORD in app does not fall back to hardcoded plaintext password."""
    import inspect
    import backend.app as app_module
    source = inspect.getsource(app_module)
    assert "zqjl piud eqwi guci" not in source


def test_no_hardcoded_neon_url_password():
    """Verify default Neon URL in pg_db does not hardcode database password."""
    import pg_db
    neon_url = getattr(pg_db, "_DEFAULT_NEON_URL", "") or ""
    assert "npg_CZLzOatv1F5l" not in neon_url
    assert "neondb_owner:" not in neon_url


def test_no_hardcoded_turso_token_in_database():
    """Verify database.py get_db does not fallback to hardcoded JWT token when env var is missing."""
    import database
    import inspect
    source = inspect.getsource(database.get_db)
    assert "eyJhbGciOiJFZERTQS" not in source
