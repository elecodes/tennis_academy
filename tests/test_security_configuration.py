import sqlite3
import pytest
from backend.app import app, init_db

@pytest.fixture
def test_db_conn(tmp_path, monkeypatch):
    """Set up isolated DB for security config testing."""
    db_file = tmp_path / "test_sec_config.db"

    monkeypatch.setenv("TURSO_URL", "")
    monkeypatch.setenv("TURSO_TOKEN", "")
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("NEON_DATABASE_URL", "")

    import pg_db
    monkeypatch.setattr(pg_db, "_DATABASE_URL", None)
    monkeypatch.setattr(pg_db, "is_pg_available", lambda: False)

    conn_pool = []

    def get_test_db():
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        conn_pool.append(conn)
        return conn

    monkeypatch.setattr("backend.app.get_db", get_test_db)
    monkeypatch.setattr("backend.database.get_db", get_test_db)

    with app.app_context():
        init_db()

    yield db_file

    for c in conn_pool:
        try:
            c.close()
        except Exception:
            pass


@pytest.fixture
def client(test_db_conn):
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client


def test_404_error_handler_prevents_stack_leak(client):
    """404 error handler should return status 404 and clean message without stack trace."""
    response = client.get("/nonexistent-endpoint-xyz")
    assert response.status_code == 404
    text = response.get_data(as_text=True)
    assert "Page not found" in text or "Error" in text
    assert "Traceback" not in text


def test_logout_clears_session(client):
    """Logout endpoint must clear session state."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["role"] = "admin"
        sess["full_name"] = "Admin User"

    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200

    with client.session_transaction() as sess:
        assert "user_id" not in sess
        assert "role" not in sess


def test_security_headers_configured(client):
    """Talisman security headers must be set."""
    response = client.get("/")
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert "Content-Security-Policy" in response.headers
