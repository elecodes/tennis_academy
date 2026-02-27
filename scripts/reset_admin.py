import sqlite3
from werkzeug.security import generate_password_hash


def reset_admin_password():
    conn = sqlite3.connect("academy.db")
    cursor = conn.cursor()
    password = generate_password_hash("tennis2026")

    # Update for all admin accounts
    cursor.execute("UPDATE users SET password = ? WHERE role='admin'", (password,))
    conn.commit()
    print(f"Admin password reset successfully for {cursor.rowcount} users.")
    conn.close()


if __name__ == "__main__":
    reset_admin_password()
