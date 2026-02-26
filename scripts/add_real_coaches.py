import sys
from werkzeug.security import generate_password_hash

# Add backend to path
sys.path.append("/Users/elena/Developer/tennis_academy/backend")

from database import get_db


def add_coaches():
    coaches = [
        {"name": "Vlad", "email": "vlad@tennis.com"},
        {"name": "Michael", "email": "michael@tennis.com"},
        {"name": "RC", "email": "rc@tennis.com"},
    ]

    conn = get_db()
    cursor = conn.cursor()

    print("Provisioning coaches in Turso Cloud...")

    for coach in coaches:
        password = generate_password_hash("tennis2026")
        try:
            # We use full_name exactly as in spreadsheet for matching
            query = (
                "INSERT INTO users (email, password, full_name, role, is_active) "
                "VALUES (?, ?, ?, 'coach', 1) "
                "ON CONFLICT(email) DO UPDATE SET full_name = excluded.full_name"
            )
            cursor.execute(query, (coach["email"], password, coach["name"]))
            print(f" - Added/Updated Coach: {coach['name']} ({coach['email']})")
        except Exception as e:
            print(f" ERROR adding {coach['name']}: {e}")

    conn.close()
    print("\nDone! Coaches are now ready for spreadsheet sync.")


if __name__ == "__main__":
    add_coaches()
