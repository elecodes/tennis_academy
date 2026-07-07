import os
import sys
from backend.pg_db import pg_query, pg_close_all, get_pg

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'coach', 'family')),
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    schedule TEXT NOT NULL,
    coach_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS group_schedules (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    court TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS group_members (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    family_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    kid_name TEXT NOT NULL,
    schedule_id INTEGER REFERENCES group_schedules(id) ON DELETE SET NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, family_id, kid_name, schedule_id)
);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL,
    message_type TEXT NOT NULL CHECK(
        message_type IN ('rain_cancellation', 'coach_delay', 'announcement', 'schedule_change')
    ),
    subject TEXT NOT NULL,
    content TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_general INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS message_recipients (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    email_sent INTEGER DEFAULT 0,
    sent_at TIMESTAMP,
    is_read INTEGER DEFAULT 0,
    ack_type TEXT,
    ack_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS family_quick_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL,
    kid_name TEXT NOT NULL,
    coach_name TEXT,
    preset TEXT NOT NULL,
    subject TEXT NOT NULL,
    content TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read INTEGER DEFAULT 0,
    deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS app_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def create_schema():
    for stmt in SCHEMA_SQL.split(";"):
        stmt = stmt.strip()
        if stmt:
            try:
                pg_query(stmt)
            except Exception as e:
                # Catch SERIAL/SEQUENCE creation errors for existing tables
                if "already exists" not in str(e).lower():
                    raise
    print("Schema created successfully.")


def migrate_data():
    from backend.database import get_db
    from backend.pg_db import _parse_url
    import pg8000

    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        print("No DATABASE_URL set — skipping migration.")
        return

    turso = get_db()
    params = _parse_url(DATABASE_URL)
    pg = pg8000.connect(**params, timeout=10)
    pg.autocommit = False

    # Clear existing data for clean migration
    cur = pg.cursor()
    # Disable FK triggers during migration (Turso has no FK enforcement)
    cur.execute("SET session_replication_role = 'replica'")
    # Drop unique constraints that conflict with Turso data (groups.name has duplicates)
    cur.execute("ALTER TABLE groups DROP CONSTRAINT IF EXISTS groups_name_key")
    tables = ["message_recipients", "family_quick_messages", "messages", "group_members", "group_schedules", "groups", "users", "app_config"]
    for t in tables:
        cur.execute(f"TRUNCATE TABLE {t} CASCADE")
    pg.commit()

    def _turso(table, order=None):
        sql = f"SELECT * FROM {table}"
        if order:
            sql += f" ORDER BY {order}"
        return [dict(r) for r in turso.execute(sql).fetchall()]

    def _bulk_insert(table, cols, rows, batch=50):
        if not rows:
            return
        col_list = ", ".join(cols)
        n = len(cols)
        cur = pg.cursor()
        for i in range(0, len(rows), batch):
            batch_rows = rows[i : i + batch]
            placeholders = ", ".join(
                "(" + ", ".join("%s" for _ in cols) + ")" for _ in batch_rows
            )
            flat_vals = []
            for r in batch_rows:
                flat_vals.extend(r.get(c) for c in cols)
            cur.execute(
                f"INSERT INTO {table} ({col_list}) VALUES {placeholders}",
                flat_vals,
            )
        pg.commit()
        print(f"  {table}: {len(rows)} rows")

    print("Migrating users...")
    _bulk_insert("users", ["id", "email", "password", "full_name", "role", "phone", "created_at", "is_active"], _turso("users", "id"))

    print("Migrating groups...")
    _bulk_insert("groups", ["id", "name", "schedule", "coach_id", "description", "created_at"], _turso("groups", "id"))

    print("Migrating group_schedules...")
    _bulk_insert("group_schedules", ["id", "group_id", "day_of_week", "start_time", "end_time", "court", "created_at", "updated_at"], _turso("group_schedules", "id"))

    print("Migrating group_members...")
    _bulk_insert("group_members", ["id", "group_id", "family_id", "kid_name", "schedule_id", "enrolled_at"], _turso("group_members", "id"))

    print("Migrating messages...")
    _bulk_insert("messages", ["id", "sender_id", "group_id", "message_type", "subject", "content", "sent_at", "is_general"], _turso("messages", "id"))

    print("Migrating message_recipients...")
    _bulk_insert("message_recipients", ["id", "message_id", "user_id", "email_sent", "sent_at", "is_read", "ack_type", "ack_at"], _turso("message_recipients", "id"))

    print("Migrating family_quick_messages...")
    _bulk_insert("family_quick_messages", ["id", "user_id", "group_id", "kid_name", "coach_name", "preset", "subject", "content", "sent_at", "is_read", "deleted_at"], _turso("family_quick_messages", "id"))

    print("Migrating app_config...")
    _bulk_insert("app_config", ["key", "value", "updated_at"], _turso("app_config", "key"))

    # Re-enable FK triggers
    cur = pg.cursor()
    cur.execute("SET session_replication_role = 'origin'")
    # Re-create unique constraint on groups.name (with deduplication)
    cur.execute("DELETE FROM groups a USING groups b WHERE a.id < b.id AND a.name = b.name")
    cur.execute("ALTER TABLE groups ADD CONSTRAINT groups_name_key UNIQUE (name)")
    pg.commit()

    pg.close()
    print("Migration complete.")


if __name__ == "__main__":
    import sys
    if "create" in sys.argv:
        create_schema()
    if "migrate" in sys.argv:
        migrate_data()
    if not any(a in sys.argv for a in ["create", "migrate"]):
        print("Usage: python3 -m backend.pg_migrate [create] [migrate]")
