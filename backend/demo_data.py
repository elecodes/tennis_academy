"""
Demo Data Script for SF TENNIS KIDS Club
Run this to populate the database with sample data for testing.
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "academy.db")


def add_demo_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear existing data (optional - remove if you want to keep existing)
    cursor.execute("DELETE FROM message_recipients")
    cursor.execute("DELETE FROM messages")
    cursor.execute("DELETE FROM group_members")
    cursor.execute("DELETE FROM groups")
    cursor.execute("DELETE FROM users WHERE role != 'admin'")
    conn.commit()

    print("Adding demo coaches...")
    coaches = [
        ("coach1@tennis.com", "password123", "John Smith", "coach", "555-0101"),
        ("coach2@tennis.com", "password123", "Sarah Johnson", "coach", "555-0102"),
    ]

    coach_ids = []
    for email, pwd, name, role, phone in coaches:
        try:
            cursor.execute(
                """
                INSERT INTO users (email, password, full_name, role, phone)
                VALUES (?, ?, ?, ?, ?)
            """,
                (email, generate_password_hash(pwd), name, role, phone),
            )
            coach_ids.append(cursor.lastrowid)
            print(f"  Added coach: {name} ({email})")
        except sqlite3.IntegrityError:
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            coach_ids.append(cursor.fetchone()[0])
            print(f"  Coach already exists: {name}")

    print("\nAdding demo families...")
    families = [
        ("family1@email.com", "password123", "Michael Brown", "family", "555-0201"),
        ("family2@email.com", "password123", "Emily Davis", "family", "555-0202"),
        ("family3@email.com", "password123", "Robert Wilson", "family", "555-0203"),
        ("family4@email.com", "password123", "Lisa Martinez", "family", "555-0204"),
    ]

    family_ids = []
    for email, pwd, name, role, phone in families:
        try:
            cursor.execute(
                """
                INSERT INTO users (email, password, full_name, role, phone)
                VALUES (?, ?, ?, ?, ?)
            """,
                (email, generate_password_hash(pwd), name, role, phone),
            )
            family_ids.append(cursor.lastrowid)
            print(f"  Added family: {name} ({email})")
        except sqlite3.IntegrityError:
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            family_ids.append(cursor.fetchone()[0])
            print(f"  Family already exists: {name}")

    print("\nAdding demo groups...")
    groups = [
        (
            "Beginners Mon/Wed",
            "Monday & Wednesday 4:00-5:30 PM",
            coach_ids[0],
            "Ages 5-7, beginner level",
        ),
        (
            "Intermediate Tue/Thu",
            "Tuesday & Thursday 4:00-5:30 PM",
            coach_ids[0],
            "Ages 8-10, intermediate level",
        ),
        (
            "Advanced Mon/Wed",
            "Monday & Wednesday 5:30-7:00 PM",
            coach_ids[1],
            "Ages 11-14, advanced level",
        ),
        (
            "Weekend Warriors",
            "Saturday 9:00-11:00 AM",
            coach_ids[1],
            "All ages, recreational",
        ),
    ]

    group_ids = []
    for name, schedule, coach_id, desc in groups:
        try:
            cursor.execute(
                """
                INSERT INTO groups (name, schedule, coach_id, description)
                VALUES (?, ?, ?, ?)
            """,
                (name, schedule, coach_id, desc),
            )
            group_ids.append(cursor.lastrowid)
            print(f"  Added group: {name}")
        except sqlite3.IntegrityError:
            print(f"  Group already exists: {name}")

    print("\nAdding demo enrollments...")
    enrollments = [
        (group_ids[0], family_ids[0], "Tommy Brown"),
        (group_ids[0], family_ids[1], "Emma Davis"),
        (group_ids[1], family_ids[2], "Alex Wilson"),
        (group_ids[2], family_ids[3], "Sophia Martinez"),
        (group_ids[3], family_ids[0], "Tommy Brown"),
        (group_ids[3], family_ids[2], "Alex Wilson"),
    ]

    for group_id, family_id, kid_name in enrollments:
        try:
            cursor.execute(
                """
                INSERT INTO group_members (group_id, family_id, kid_name)
                VALUES (?, ?, ?)
            """,
                (group_id, family_id, kid_name),
            )
            print(f"  Enrolled {kid_name} in group {group_id}")
        except sqlite3.IntegrityError:
            print(f"  Enrollment already exists: {kid_name} in group {group_id}")

    conn.commit()
    conn.close()

    print("\n" + "=" * 50)
    print("Demo data added successfully!")
    print("=" * 50)
    print("\nYou can now log in with:")
    print("\nAdmin (create at /setup):")
    print("  Create your own admin account")
    print("\nCoaches:")
    print("  coach1@tennis.com / password123")
    print("  coach2@tennis.com / password123")
    print("\nFamilies:")
    print("  family1@email.com / password123")
    print("  family2@email.com / password123")
    print("  family3@email.com / password123")
    print("  family4@email.com / password123")


if __name__ == "__main__":
    add_demo_data()
