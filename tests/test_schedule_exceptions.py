import sqlite3
import pytest
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
