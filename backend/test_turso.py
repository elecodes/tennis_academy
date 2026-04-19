from database import get_db

conn = get_db()
users = conn.execute("SELECT email, password FROM users").fetchall()
for u in users:
    print(u)
