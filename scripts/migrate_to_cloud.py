import sys
import os
import sqlite3

# Add backend to path
sys.path.append("/Users/elena/Developer/tennis_academy/backend")

from database import get_db


def migrate():
    # Local DB path
    local_db_path = "/Users/elena/Developer/tennis_academy/academy.db"

    if not os.path.exists(local_db_path):
        print(f"ERROR: Local database not found at {local_db_path}")
        return

    print("Connecting to databases...")
    local_conn = sqlite3.connect(local_db_path)
    local_conn.row_factory = sqlite3.Row
    local_cursor = local_conn.cursor()

    cloud_conn = get_db()
    cloud_cursor = cloud_conn.cursor()

    def row_to_dict(row):
        return {key: row[key] for key in row.keys()}

    # 1. Migrate Users
    print("Migrating users...")
    local_cursor.execute("SELECT * FROM users")
    users = local_cursor.fetchall()
    for user_row in users:
        user = row_to_dict(user_row)
        try:
            query = (
                "INSERT INTO users (id, email, password, full_name, role, phone, created_at, is_active) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(email) DO NOTHING"
            )
            cloud_cursor.execute(
                query,
                (
                    user["id"],
                    user["email"],
                    user["password"],
                    user["full_name"],
                    user["role"],
                    user.get("phone"),
                    user["created_at"],
                    user["is_active"],
                ),
            )
        except Exception as e:
            print(f"  Warning inserting user {user['email']}: {e}")

    # 2. Migrate Groups
    print("Migrating groups...")
    local_cursor.execute("SELECT * FROM groups")
    groups = local_cursor.fetchall()
    for group_row in groups:
        group = row_to_dict(group_row)
        try:
            query = (
                "INSERT INTO groups (id, name, schedule, coach_id, description, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(name) DO NOTHING"
            )
            cloud_cursor.execute(
                query,
                (
                    group["id"],
                    group["name"],
                    group["schedule"],
                    group["coach_id"],
                    group["description"],
                    group["created_at"],
                ),
            )
        except Exception as e:
            print(f"  Warning inserting group {group['name']}: {e}")

    # 3. Migrate Group Members
    print("Migrating group members...")
    local_cursor.execute("SELECT * FROM group_members")
    members = local_cursor.fetchall()
    for m_row in members:
        m = row_to_dict(m_row)
        try:
            query = (
                "INSERT INTO group_members (id, group_id, family_id, kid_name, enrolled_at) "
                "VALUES (?, ?, ?, ?, ?) ON CONFLICT DO NOTHING"
            )
            cloud_cursor.execute(
                query,
                (
                    m["id"],
                    m["group_id"],
                    m["family_id"],
                    m["kid_name"],
                    m["enrolled_at"],
                ),
            )
        except Exception as e:
            print(f"  Warning inserting member: {e}")

    print("\nMigration completed!")
    local_conn.close()
    cloud_conn.close()


if __name__ == "__main__":
    migrate()
