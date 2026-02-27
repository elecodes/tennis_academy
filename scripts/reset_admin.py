import sys
import os

# Ensure backend can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from werkzeug.security import generate_password_hash
from database import get_db


def reset_passwords():
    print("Connecting to Turso Cloud...")
    conn = get_db()

    password_hash = generate_password_hash("tennis2026")

    admin_res = conn.execute(
        "UPDATE users SET password = ? WHERE role = 'admin'", (password_hash,)
    )
    family_res = conn.execute(
        "UPDATE users SET password = ? WHERE role = 'family'", (password_hash,)
    )

    print(f"Updated admins. Affected rows: {getattr(admin_res, 'rowcount', 'unknown')}")
    print(
        f"Updated families. Affected rows: {getattr(family_res, 'rowcount', 'unknown')}"
    )

    # Check what users exist
    families = conn.execute(
        "SELECT id, email FROM users WHERE role = 'family'"
    ).fetchall()
    admins = conn.execute("SELECT id, email FROM users WHERE role = 'admin'").fetchall()
    print("Families found:", [f["email"] for f in families])
    print("Admins found:", [a["email"] for a in admins])


if __name__ == "__main__":
    reset_passwords()
