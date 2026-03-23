#!/usr/bin/env python3
"""
Direct Google Sheets to Turso Sync Script
Bypasses Apps Script - syncs directly via Google Sheets API
"""

import os
from dotenv import load_dotenv

load_dotenv()

from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests

# Config
CREDENTIALS_FILE = "google-sheets-key.json"
SPREADSHEET_ID = "1pnJWsdaALpM9NghSXM41O0yM29FMgXDCPgRnbbceQBU"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TURSO_URL = (
    os.environ.get("TURSO_URL").replace("libsql://", "https://") + "/v2/pipeline"
)
TURSO_TOKEN = os.environ.get("TURSO_TOKEN")

DAYS_MAP = {
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


def turso_query(sql, params=None):
    """Execute SQL on Turso"""
    payload = {
        "requests": [{"type": "execute", "stmt": {"sql": sql, "args": (params or [])}}]
    }
    r = requests.post(
        TURSO_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {TURSO_TOKEN}",
            "Content-Type": "application/json",
        },
    )
    return r.json()


def get_coach_id(coach_name):
    """Find coach by name"""
    if not coach_name:
        return None
    result = turso_query(
        "SELECT id FROM users WHERE full_name = ? AND role = 'coach' LIMIT 1",
        [{"type": "text", "value": coach_name}],
    )
    rows = result["results"][0]["response"]["result"]["rows"]
    if rows:
        return int(rows[0][0]["value"])
    return None


def get_or_create_group(group_name, coach_id):
    """Find or create a group"""
    if not group_name or group_name == "Group":
        group_name = "General Group"

    # Try to find existing
    if coach_id:
        result = turso_query(
            "SELECT id FROM groups WHERE name = ? AND coach_id = ? LIMIT 1",
            [
                {"type": "text", "value": group_name},
                {"type": "integer", "value": str(coach_id)},
            ],
        )
    else:
        result = turso_query(
            "SELECT id FROM groups WHERE name = ? LIMIT 1",
            [{"type": "text", "value": group_name}],
        )

    rows = result["results"][0]["response"]["result"]["rows"]
    if rows:
        return int(rows[0][0]["value"])

    # Create new group
    turso_query(
        "INSERT INTO groups (name, coach_id, schedule) VALUES (?, ?, '')",
        [
            {"type": "text", "value": group_name},
            {"type": "integer", "value": str(coach_id)}
            if coach_id
            else {"type": "null"},
        ],
    )
    result = turso_query("SELECT last_insert_rowid()")
    return int(result["results"][0]["response"]["result"]["rows"][0][0]["value"])


def get_or_create_family(email, name, phone=None, kid_name=None):
    """Find or create a family user by email, name, or kid_name"""
    family_id = None

    # Try email first if available
    if email and "@" in email:
        result = turso_query(
            "SELECT id FROM users WHERE email = ?", [{"type": "text", "value": email}]
        )
        rows = result["results"][0]["response"]["result"]["rows"]
        if rows:
            return int(rows[0][0]["value"])

    # Try name if email didn't work
    lookup_name = name if name else kid_name
    if lookup_name:
        # Normalize name for lookup
        normalized_name = lookup_name.strip().lower()
        result = turso_query(
            "SELECT id FROM users WHERE LOWER(full_name) = ? AND role = 'family'",
            [{"type": "text", "value": normalized_name}],
        )
        rows = result["results"][0]["response"]["result"]["rows"]
        if rows:
            return int(rows[0][0]["value"])

        # Create new family using name as identifier
        family_name = lookup_name.strip()
        family_email = (
            email
            if email and "@" in email
            else f"{normalized_name.replace(' ', '.').replace('&', 'and').replace('@', '')}@tennis.local"
        )

        result = turso_query(
            "INSERT INTO users (email, full_name, role, password, phone) VALUES (?, ?, 'family', 'sync123', ?)",
            [
                {"type": "text", "value": family_email},
                {"type": "text", "value": family_name},
                {"type": "text", "value": phone}
                if phone
                else {"type": "null", "value": None},
            ],
        )
        result = turso_query("SELECT last_insert_rowid()")
        return int(result["results"][0]["response"]["result"]["rows"][0][0]["value"])

    return None


def add_schedule(group_id, day_of_week, start_time, coach_id):
    """Add a session schedule if it doesn't already exist"""
    if not coach_id:
        return
    # Check if schedule already exists
    normalized_time = (
        start_time.lower().replace(" ", "").replace(":00", "").replace(":", "")
    )
    result = turso_query(
        "SELECT id FROM group_schedules WHERE group_id = ? AND day_of_week = ? AND start_time = ?",
        [
            {"type": "integer", "value": str(group_id)},
            {"type": "integer", "value": str(day_of_week)},
            {"type": "text", "value": start_time},
        ],
    )
    rows = result["results"][0]["response"]["result"]["rows"]
    if rows:
        return  # Already exists, don't duplicate
    turso_query(
        "INSERT INTO group_schedules (group_id, day_of_week, start_time, end_time, court) VALUES (?, ?, ?, ?, 'Court 1')",
        [
            {"type": "integer", "value": str(group_id)},
            {"type": "integer", "value": str(day_of_week)},
            {"type": "text", "value": start_time},
            {"type": "text", "value": start_time},
        ],
    )


def get_schedule_id(group_id, day_of_week, start_time):
    """Find schedule ID by group, day, and time"""
    # Normalize time for comparison
    normalized_time = (
        start_time.lower().replace(" ", "").replace(":00", "").replace(":", "")
    )
    result = turso_query(
        "SELECT id, start_time FROM group_schedules WHERE group_id = ? AND day_of_week = ?",
        [
            {"type": "integer", "value": str(group_id)},
            {"type": "integer", "value": str(day_of_week)},
        ],
    )
    rows = result["results"][0]["response"]["result"]["rows"]
    for row in rows:
        sched_time = (
            row[1]["value"].lower().replace(" ", "").replace(":00", "").replace(":", "")
        )
        if sched_time == normalized_time:
            return int(row[0]["value"])
    # No exact match found
    return None


def add_enrollment(group_id, family_id, kid_name, schedule_id=None):
    """Add enrollment with optional schedule_id"""
    if not family_id or not kid_name:
        return
    if schedule_id:
        turso_query(
            "INSERT OR IGNORE INTO group_members (group_id, family_id, kid_name, schedule_id) VALUES (?, ?, ?, ?)",
            [
                {"type": "integer", "value": str(group_id)},
                {"type": "integer", "value": str(family_id)},
                {"type": "text", "value": kid_name},
                {"type": "integer", "value": str(schedule_id)},
            ],
        )
    else:
        turso_query(
            "INSERT OR IGNORE INTO group_members (group_id, family_id, kid_name) VALUES (?, ?, ?)",
            [
                {"type": "integer", "value": str(group_id)},
                {"type": "integer", "value": str(family_id)},
                {"type": "text", "value": kid_name},
            ],
        )


def clean_time(time_str):
    """Clean time string to h:mm am/pm format (12-hour)"""
    if not time_str:
        return ""
    time_str = str(time_str).strip().lower()
    # Handle already formatted times
    if "am" in time_str or "pm" in time_str:
        return time_str.replace(" ", "")
    # Parse HH:MM:SS or HH:MM format
    import re

    match = re.match(r"(\d{1,2}):(\d{2})(?::\d{2})?", time_str)
    if match:
        hour = int(match.group(1))
        minute = match.group(2)
        # Convert 24-hour to 12-hour
        if hour >= 12:
            period = "pm"
            if hour > 12:
                hour -= 12
        else:
            period = "am"
            if hour == 0:
                hour = 12
        return f"{hour}:{minute}{period}"
    return time_str


def update_group_schedule_summaries():
    """Build schedule summaries from group_schedules and update groups.schedule"""
    DAYS = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    # Get all groups with their schedules
    result = turso_query("""
        SELECT g.id, g.name, gs.day_of_week, gs.start_time
        FROM groups g
        JOIN group_schedules gs ON g.id = gs.group_id
        WHERE g.coach_id IS NOT NULL
        ORDER BY g.id, gs.day_of_week, gs.start_time
    """)

    rows = result["results"][0]["response"]["result"]["rows"]

    # Group by group_id
    group_schedules = {}
    for row in rows:
        gid = row[0]["value"]
        day = int(row[2]["value"])
        time = row[3]["value"]
        if gid not in group_schedules:
            group_schedules[gid] = []
        group_schedules[gid].append((day, time))

    # Build summaries and update
    for gid, schedules in group_schedules.items():
        # Sort by day
        schedules.sort()
        # Build summary like "Mon 4pm, Wed 5pm, Sat 9am"
        days_short = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        summary_parts = []
        for day, time in schedules:
            summary_parts.append(f"{days_short[day]} {time}")
        summary = ", ".join(summary_parts)

        # Update groups.schedule
        turso_query(
            "UPDATE groups SET schedule = ? WHERE id = ?",
            [
                {"type": "text", "value": summary},
                {"type": "integer", "value": str(gid)},
            ],
        )
        print(f"    Updated group {gid}: {summary}")


def sync():
    """Main sync function"""
    print("🔄 Starting Google Sheets sync...")

    # Clear existing schedules
    print("  Clearing old schedules...")
    turso_query("DELETE FROM group_schedules")
    turso_query("DELETE FROM group_members")

    # Clear orphaned groups (no coach)
    turso_query("DELETE FROM groups WHERE coach_id IS NULL")

    # Get spreadsheet data
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=creds)

    # Get all day sheets
    days = [
        "MONDAY",
        "TUESDAY",
        "WEDNESDAYS",
        "THURSDAY",
        "FRIDAY",
        "SATURDAY",
        "SUNDAY",
    ]

    total_sessions = 0
    total_enrollments = 0

    for day_name in days:
        day_lower = day_name.lower()
        day_num = None
        for d, n in DAYS_MAP.items():
            if d in day_lower:
                day_num = n
                break

        if day_num is None:
            continue

        print(f"\n📅 {day_name}:")

        try:
            result = (
                service.spreadsheets()
                .values()
                .get(spreadsheetId=SPREADSHEET_ID, range=f"{day_name}!A:J")
                .execute()
            )

            values = result.get("values", [])

            # Track current slot context (for continuation rows)
            current_time = None
            current_coach = None
            current_group = None
            current_coach_id = None
            current_group_id = None
            current_schedule_id = None

            for i, row in enumerate(values):
                if i == 0:  # Skip header
                    continue
                if not row:
                    continue

                raw_time = row[0] if len(row) > 0 else ""
                raw_coach = row[1] if len(row) > 1 else ""
                raw_group = row[2] if len(row) > 2 else ""
                raw_kid = row[3] if len(row) > 3 else ""

                time = clean_time(raw_time) if raw_time else ""
                coach_name = str(raw_coach).strip() if raw_coach else ""
                group_name = str(raw_group).strip() if raw_group else ""
                kid_name = str(raw_kid).strip() if raw_kid else ""
                parent_name = str(row[7]).strip() if len(row) > 7 and row[7] else ""
                parent_email = str(row[8]).strip() if len(row) > 8 and row[8] else ""
                parent_phone = str(row[9]).strip() if len(row) > 9 and row[9] else ""

                # Skip header rows (don't update context!)
                if "time" in time.lower() or "coach" in coach_name.lower():
                    continue

                # Skip rows with no meaningful data
                if not time and not coach_name and not group_name and not kid_name:
                    continue

                # If this row has new time/coach/group, update context
                if time and coach_name and group_name:
                    current_time = time
                    current_coach = coach_name
                    current_group = group_name

                    # Get coach and group IDs
                    current_coach_id = get_coach_id(current_coach)
                    if current_coach_id:
                        current_group_id = get_or_create_group(
                            current_group, current_coach_id
                        )
                        # Add schedule
                        add_schedule(
                            current_group_id, day_num, current_time, current_coach_id
                        )
                        total_sessions += 1
                        # Get schedule_id
                        current_schedule_id = get_schedule_id(
                            current_group_id, day_num, current_time
                        )

                # Skip if no kid name
                if not kid_name:
                    continue

                # Only add enrollment if this row has an explicit group (not a continuation row)
                if not group_name:
                    continue  # Skip continuation rows with kids but no group indicator

                # Skip if coach not found
                if not current_coach_id:
                    continue

                print(
                    f"  {current_time} | {current_coach} | {current_group} | {kid_name}"
                )

                # Add enrollment with schedule_id
                family_id = get_or_create_family(
                    parent_email, parent_name or kid_name, parent_phone
                )
                if family_id:
                    add_enrollment(
                        current_group_id, family_id, kid_name, current_schedule_id
                    )
                    total_enrollments += 1

        except Exception as e:
            print(f"  ❌ Error reading {day_name}: {e}")

    # Update groups.schedule text field from group_schedules
    print("\n  Updating group schedule summaries...")
    update_group_schedule_summaries()

    print(f"\n✅ Sync complete!")
    print(f"   Sessions: {total_sessions}")
    print(f"   Enrollments: {total_enrollments}")


if __name__ == "__main__":
    sync()
