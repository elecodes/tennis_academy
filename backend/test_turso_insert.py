from database import get_db
from werkzeug.security import generate_password_hash
import uuid

conn = get_db()
test_email = f"test_{uuid.uuid4().hex[:8]}@test.com"
password = "password123"
hashed = generate_password_hash(password)

conn.execute(
    "INSERT INTO users (email, password, full_name, role, phone, is_active) VALUES (?, ?, ?, ?, ?, ?)",
    (test_email, hashed, "Test Admin", "admin", "123", 1)
)
print(f"Created user {test_email} with password {password}")
