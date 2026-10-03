import sqlite3
import pytest
from werkzeug.security import generate_password_hash
from backend.app import app, init_db

@pytest.fixture
def test_db_conn(tmp_path, monkeypatch):
    """Set up an isolated SQLite database for testing and override get_db and academy_db."""
    db_file = tmp_path / "test_rbac.db"
    
    # Force env vars to empty strings so Postgres/Turso paths in init_db are bypassed
    monkeypatch.setenv("TURSO_URL", "")
    monkeypatch.setenv("TURSO_TOKEN", "")
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("NEON_DATABASE_URL", "")

    import pg_db
    monkeypatch.setattr(pg_db, "_DATABASE_URL", None)
    monkeypatch.setattr(pg_db, "is_pg_available", lambda: False)

    # Mock external Supabase/Academy DB calls to return empty lists cleanly
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

    # Initialize schema
    with app.app_context():
        init_db()

    conn = get_test_db()
    # Create test users
    admin_pw = generate_password_hash("admin123")
    coach1_pw = generate_password_hash("coach123")
    coach2_pw = generate_password_hash("coach123")
    family_pw = generate_password_hash("family123")

    conn.execute(
        "INSERT INTO users (id, email, password, full_name, role) VALUES (1, 'admin@test.com', ?, 'Admin User', 'admin')",
        (admin_pw,),
    )
    conn.execute(
        "INSERT INTO users (id, email, password, full_name, role) VALUES (2, 'coach1@test.com', ?, 'Coach One', 'coach')",
        (coach1_pw,),
    )
    conn.execute(
        "INSERT INTO users (id, email, password, full_name, role) VALUES (3, 'coach2@test.com', ?, 'Coach Two', 'coach')",
        (coach2_pw,),
    )
    conn.execute(
        "INSERT INTO users (id, email, password, full_name, role) VALUES (4, 'family@test.com', ?, 'Family User', 'family')",
        (family_pw,),
    )

    # Create test groups
    conn.execute(
        "INSERT INTO groups (id, name, schedule, coach_id) VALUES (1, 'Group Coach 1', 'Mon 4pm', 2)"
    )
    conn.execute(
        "INSERT INTO groups (id, name, schedule, coach_id) VALUES (2, 'Group Coach 2', 'Tue 4pm', 3)"
    )

    # Create a quick message for Coach 1
    conn.execute(
        """INSERT INTO family_quick_messages (id, user_id, group_id, kid_name, coach_name, preset, subject, content)
           VALUES (100, 4, 1, 'Tommy', 'Coach One', 'running_late', 'Running Late', 'On our way')"""
    )

    conn.commit()
    conn.close()

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


def test_unauthenticated_cannot_access_debug_sync_status(client):
    """Unauthenticated users must not access debug sync status PII."""
    response = client.get("/api/debug/sync-status")
    assert response.status_code in (302, 401, 403)


def test_unauthenticated_cannot_access_debug_pg_check(client):
    """Unauthenticated users must not access debug pg check."""
    response = client.get("/api/debug/pg-check")
    assert response.status_code in (302, 401, 403)


def test_family_cannot_access_debug_sync_status(client):
    """Family role must not access debug sync status PII."""
    client.post("/login", data={"email": "family@test.com", "password": "family123"})
    response = client.get("/api/debug/sync-status")
    assert response.status_code in (302, 401, 403)


def test_admin_can_access_debug_sync_status(client):
    """Admin role can access debug sync status."""
    client.post("/login", data={"email": "admin@test.com", "password": "admin123"})
    response = client.get("/api/debug/sync-status")
    assert response.status_code == 200


def test_coach_cannot_reply_to_other_coach_quick_message(client):
    """Coach 2 should NOT be allowed to reply to Coach 1's quick message (IDOR prevention)."""
    client.post("/login", data={"email": "coach2@test.com", "password": "coach123"})
    
    response = client.post(
        "/coach/reply-family/100",
        data={"content": "Malicious reply from unauthorized coach"},
        follow_redirects=True,
    )
    
    content_text = response.get_data(as_text=True)
    assert "Unauthorized" in content_text or "Access denied" in content_text or "not authorized" in content_text.lower() or response.status_code in (403, 302)


def test_admin_can_delete_family_quick_message(client):
    """Admin can delete a family quick message using CURRENT_TIMESTAMP."""
    client.post("/login", data={"email": "admin@test.com", "password": "admin123"})
    response = client.post(
        "/admin/messages/100/delete",
        data={"source": "family_note"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Message deleted." in response.get_data(as_text=True)


def test_non_admin_cannot_delete_message(client):
    """Coach and Family roles must not be able to delete messages."""
    client.post("/login", data={"email": "coach1@test.com", "password": "coach123"})
    response = client.post(
        "/admin/messages/100/delete",
        data={"source": "family_note"},
    )
    assert response.status_code in (302, 401, 403)


