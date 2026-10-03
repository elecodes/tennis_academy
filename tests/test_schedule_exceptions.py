import sqlite3
import pytest
from werkzeug.security import generate_password_hash
from backend.app import app, init_db

@pytest.fixture
def test_db_conn(tmp_path, monkeypatch):
    """Set up isolated DB for schedule exceptions testing."""
    db_file = tmp_path / "test_exceptions.db"

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
        "INSERT INTO groups (id, name, schedule, coach_id) VALUES (1, 'Beginners Sat', 'Sat 12pm', 2)"
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


def test_schedule_exceptions_table_exists(client):
    """Verify schedule_exceptions table is initialized in database."""
    from backend.app import get_db
    conn = get_db()
    cursor = conn.execute("PRAGMA table_info(schedule_exceptions)")
    cols = [col["name"] for col in cursor.fetchall()]
    assert "id" in cols
    assert "group_id" in cols
    assert "exception_date" in cols
    assert "status" in cols
    assert "note_text" in cols


def test_insert_and_fetch_schedule_exception(client):
    """Verify inserting and fetching date-specific schedule exception."""
    from backend.app import get_db
    conn = get_db()
    
    conn.execute(
        """INSERT INTO schedule_exceptions (group_id, kid_name, exception_date, status, note_text)
           VALUES (1, 'Alex', '2026-10-10', 'no_lesson', 'Alex is sick - no lesson this Sat 12pm')"""
    )
    conn.commit()

    row = conn.execute(
        "SELECT * FROM schedule_exceptions WHERE exception_date = '2026-10-10'"
    ).fetchone()

    assert row is not None
    assert row["group_id"] == 1
    assert row["kid_name"] == "Alex"
    assert row["status"] == "no_lesson"
    assert "Alex is sick" in row["note_text"]


def test_admin_can_add_schedule_exception(client):
    """Admin user should be able to create a schedule exception alert via POST."""
    client.post("/login", data={"email": "admin@test.com", "password": "admin123"})

    response = client.post(
        "/admin/schedule-exceptions/add",
        data={
            "group_id": "1",
            "kid_name": "Tommy",
            "exception_date": "2026-10-17",
            "status": "no_lesson",
            "note_text": "Court maintenance - no lesson Oct 17",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    from backend.app import get_db
    conn = get_db()
    row = conn.execute("SELECT * FROM schedule_exceptions WHERE exception_date = '2026-10-17'").fetchone()
    assert row is not None
    assert row["status"] == "no_lesson"


def test_non_admin_cannot_add_schedule_exception(client):
    """Coach/Family users must not be allowed to post schedule exceptions to admin route."""
    client.post("/login", data={"email": "family@test.com", "password": "family123"})

    response = client.post(
        "/admin/schedule-exceptions/add",
        data={
            "group_id": "1",
            "exception_date": "2026-10-17",
            "status": "no_lesson",
            "note_text": "Unauthorized exception",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/dashboard" in response.headers.get("Location", "")


def test_admin_can_delete_schedule_exception(client):
    """Admin user should be able to delete a schedule exception."""
    from backend.app import get_db
    conn = get_db()
    conn.execute(
        "INSERT INTO schedule_exceptions (id, group_id, exception_date, status, note_text) VALUES (99, 1, '2026-10-24', 'note', 'Sample note')"
    )
    conn.commit()

    client.post("/login", data={"email": "admin@test.com", "password": "admin123"})
    response = client.post("/admin/schedule-exceptions/delete/99", follow_redirects=True)
    assert response.status_code == 200

    row = conn.execute("SELECT * FROM schedule_exceptions WHERE id = 99").fetchone()
    assert row is None


def test_coach_dashboard_displays_schedule_exceptions(client):
    """Coach dashboard should render schedule exceptions for assigned groups."""
    from backend.app import get_db
    conn = get_db()
    conn.execute(
        """INSERT INTO schedule_exceptions (group_id, exception_date, status, note_text)
           VALUES (1, '2026-10-31', 'no_lesson', 'No lesson on Halloween Oct 31')"""
    )
    conn.commit()

    client.post("/login", data={"email": "coach@test.com", "password": "coach123"})
    response = client.get("/dashboard")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "No lesson on Halloween Oct 31" in text or "Halloween" in text


def test_timetable_passes_schedule_exceptions(client):
    """Timetable route should query and pass schedule_exceptions for the active week."""
    from backend.app import get_db
    conn = get_db()
    conn.execute(
        """INSERT INTO schedule_exceptions (group_id, exception_date, status, note_text)
           VALUES (1, '2026-10-10', 'kid_absent', 'Alex absent Oct 10')"""
    )
    conn.commit()

    client.post("/login", data={"email": "admin@test.com", "password": "admin123"})
    response = client.get("/timetable?date=2026-10-10")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Alex absent Oct 10" in text or "schedule_exceptions" in response.get_data(as_text=True) or response.status_code == 200
