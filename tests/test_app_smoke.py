import sqlite3
import pytest
from werkzeug.security import generate_password_hash
from backend.app import app, init_db

@pytest.fixture
def test_db_conn(tmp_path, monkeypatch):
    """Set up clean SQLite test DB and mock external services."""
    db_file = tmp_path / "smoke_test.db"

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
    monkeypatch.setattr(academy_db, "fetch_family_enrollments", lambda email: [])
    monkeypatch.setattr(academy_db, "fetch_timetable", lambda *args, **kwargs: {"groups": []})

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

    conn = get_test_db()
    admin_pw = generate_password_hash("admin123")
    coach_pw = generate_password_hash("coach123")
    family_pw = generate_password_hash("family123")

    conn.execute(
        "INSERT INTO users (id, email, password, full_name, role) VALUES (1, 'admin@test.com', ?, 'Admin User', 'admin')",
        (admin_pw,),
    )
    conn.execute(
        "INSERT INTO users (id, email, password, full_name, role) VALUES (2, 'coach@test.com', ?, 'Coach Smith', 'coach')",
        (coach_pw,),
    )
    conn.execute(
        "INSERT INTO users (id, email, password, full_name, role) VALUES (3, 'family@test.com', ?, 'Family Jones', 'family')",
        (family_pw,),
    )

    conn.execute(
        "INSERT INTO groups (id, name, schedule, coach_id) VALUES (1, 'Junior Beginners', 'Mon 4pm', 2)"
    )
    conn.execute(
        "INSERT INTO group_schedules (id, group_id, day_of_week, start_time, end_time, court) VALUES (1, 1, 0, '16:00', '17:00', 'Court 1')"
    )
    conn.execute(
        "INSERT INTO group_members (id, group_id, family_id, kid_name, schedule_id) VALUES (1, 1, 3, 'Alex', 1)"
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


def test_public_routes_work(client):
    """Test public landing and login pages."""
    resp = client.get("/")
    assert resp.status_code in (200, 302)

    resp = client.get("/login")
    assert resp.status_code == 200
    assert "Login" in resp.get_data(as_text=True) or "Sign In" in resp.get_data(as_text=True)


def test_admin_flow_works(client):
    """Test login and core admin dashboard and management pages."""
    resp = client.post("/login", data={"email": "admin@test.com", "password": "admin123"}, follow_redirects=True)
    assert resp.status_code == 200

    for path in ["/dashboard", "/admin/users", "/admin/groups", "/admin/enrollments"]:
        res = client.get(path)
        assert res.status_code == 200, f"Failed for path: {path}"


def test_coach_flow_works(client):
    """Test coach dashboard and my-groups pages."""
    resp = client.post("/login", data={"email": "coach@test.com", "password": "coach123"}, follow_redirects=True)
    assert resp.status_code == 200

    for path in ["/dashboard", "/coach/my-groups", "/timetable"]:
        res = client.get(path)
        assert res.status_code == 200, f"Failed for path: {path}"


def test_family_flow_works(client):
    """Test family dashboard, messages, and enrollments pages."""
    resp = client.post("/login", data={"email": "family@test.com", "password": "family123"}, follow_redirects=True)
    assert resp.status_code == 200

    for path in ["/dashboard", "/family/my-messages", "/family/my-enrollments", "/timetable"]:
        res = client.get(path)
        assert res.status_code == 200, f"Failed for path: {path}"
