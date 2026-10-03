import sqlite3
import pytest
from html import escape
from backend.app import app, init_db

@pytest.fixture
def test_db_conn(tmp_path, monkeypatch):
    """Set up an isolated SQLite database for injection resistance testing."""
    db_file = tmp_path / "test_injection.db"
    
    monkeypatch.setenv("TURSO_URL", "")
    monkeypatch.setenv("TURSO_TOKEN", "")
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("NEON_DATABASE_URL", "")

    import pg_db
    monkeypatch.setattr(pg_db, "_DATABASE_URL", None)
    monkeypatch.setattr(pg_db, "is_pg_available", lambda: False)

    import academy_db
    monkeypatch.setattr(academy_db, "fetch_lessons", lambda: [])
    monkeypatch.setattr(academy_db, "fetch_coaches", lambda: [])
    monkeypatch.setattr(academy_db, "fetch_students", lambda: [])
    monkeypatch.setattr(academy_db, "fetch_coach_lessons", lambda name: [])
    monkeypatch.setattr(academy_db, "fetch_student_lessons", lambda: [])

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


def test_sql_injection_attempt_in_login(client):
    """Attempt SQL injection payload in login email field."""
    malicious_email = "' OR '1'='1' --"
    response = client.post(
        "/login",
        data={"email": malicious_email, "password": "password123"},
        follow_redirects=True,
    )
    # Must fail safely without bypass or SQL error crash
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert "Invalid email or password" in content or "Please log in" in content


def test_xss_payload_escaped_in_html_rendering(client):
    """Verify script tags in user inputs are HTML-escaped by Jinja2 renderer."""
    xss_payload = "<script>alert('xss')</script>"
    escaped_payload = escape(xss_payload)
    
    with app.test_request_context():
        rendered = app.jinja_env.from_string("Hello {{ name }}").render(name=xss_payload)
        assert "<script>" not in rendered
        assert "&lt;script&gt;" in rendered
