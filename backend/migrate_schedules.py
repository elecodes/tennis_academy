import sqlite3
import os
import re

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "academy.db")


def parse_schedule(text):
    if not text:
        return []

    days_map = {
        "monday": 0,
        "mon": 0,
        "tuesday": 1,
        "tue": 1,
        "wednesday": 2,
        "wed": 2,
        "thursday": 3,
        "thu": 3,
        "friday": 4,
        "fri": 4,
        "saturday": 5,
        "sat": 5,
        "sunday": 6,
        "sun": 6,
    }

    # Split by & or ,
    # Split by & or ,
    # parts = re.split(r"[&,]", text)

    # Extract time range or single time
    # matches 4:00-5:30 PM, 1:30pm, 9:00-11:00 AM, etc.
    time_match = re.search(
        r"(\d{1,2}:\d{2})(?:\s*-\s*(\d{1,2}:\d{2}))?\s*(am|pm)?", text, re.IGNORECASE
    )

    start_time = "16:00"  # Default
    end_time = "17:30"  # Default

    if time_match:
        start = time_match.group(1)
        end = time_match.group(2)
        meridiem = time_match.group(3)

        # Convert to 24h
        def to_24h(t, m):
            if not t:
                return t
            h, mins = map(int, t.split(":"))
            if m and m.lower() == "pm" and h < 12:
                h += 12
            if m and m.lower() == "am" and h == 12:
                h = 0
            return f"{h:02d}:{mins:02d}"

        start_time = to_24h(start, meridiem)
        if end:
            end_time = to_24h(end, meridiem)
        else:
            # If no end time, default to 1 hour after start
            h, mins = map(int, start_time.split(":"))
            end_time = f"{(h + 1) % 24:02d}:{mins:02d}"

    schedules = []

    # Only iterate through days found in text
    for day_name, day_num in days_map.items():
        if re.search(r"\b" + day_name + r"\b", text, re.IGNORECASE):
            schedules.append(
                {
                    "day": day_num,
                    "start": start_time,
                    "end": end_time,
                    "court": "Court 1",  # Default
                }
            )

    return schedules


def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Ensure table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            court TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("SELECT id, name, schedule FROM groups")
    groups = cursor.fetchall()

    for group in groups:
        print(f"Processing group: {group['name']} (Schedule: {group['schedule']})")
        schedules = parse_schedule(group["schedule"])

        for s in schedules:
            # Check if already exists to avoid duplicates
            cursor.execute(
                """
                SELECT id FROM group_schedules
                WHERE group_id = ? AND day_of_week = ? AND start_time = ?
            """,
                (group["id"], s["day"], s["start"]),
            )

            if not cursor.fetchone():
                cursor.execute(
                    """
                    INSERT INTO group_schedules (group_id, day_of_week, start_time, end_time, court)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (group["id"], s["day"], s["start"], s["end"], s["court"]),
                )
                print(f"  Added: Day {s['day']} {s['start']}-{s['end']}")
            else:
                print(f"  Skipped (already exists): Day {s['day']} {s['start']}")

    conn.commit()
    conn.close()
    print("Migration complete!")


if __name__ == "__main__":
    migrate()
