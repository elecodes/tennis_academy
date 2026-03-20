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


def get_or_create_family(email, name):
    """Find or create a family user"""
    if not email or "@" not in email:
        return None

    result = turso_query(
        "SELECT id FROM users WHERE email = ?", [{"type": "text", "value": email}]
    )
    rows = result["results"][0]["response"]["result"]["rows"]
    if rows:
        return int(rows[0][0]["value"])

    # Create new family
    family_name = name if name else "Family"
    turso_query(
        "INSERT INTO users (email, full_name, role, password) VALUES (?, ?, 'family', 'temp')",
        [{"type": "text", "value": email}, {"type": "text", "value": family_name}],
    )
    result = turso_query("SELECT last_insert_rowid()")
    return int(result["results"][0]["response"]["result"]["rows"][0][0]["value"])


def add_schedule(group_id, day_of_week, start_time, coach_id):
    """Add a session schedule"""
    if not coach_id:
        return
    turso_query(
        "INSERT INTO group_schedules (group_id, day_of_week, start_time, end_time, court) VALUES (?, ?, ?, ?, 'Court 1')",
        [
            {"type": "integer", "value": str(group_id)},
            {"type": "integer", "value": str(day_of_week)},
            {"type": "text", "value": start_time},
            {"type": "text", "value": start_time},
        ],
    )


def add_enrollment(group_id, family_id, kid_name):
    """Add enrollment"""
    if not family_id or not kid_name:
        return
    turso_query(
        "INSERT OR IGNORE INTO group_members (group_id, family_id, kid_name) VALUES (?, ?, ?)",
        [
            {"type": "integer", "value": str(group_id)},
            {"type": "integer", "value": str(family_id)},
            {"type": "text", "value": kid_name},
        ],
    )


def clean_time(time_str):
    """Clean time string to h:mm am/pm format"""
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

            for i, row in enumerate(values):
                if i == 0:  # Skip header
                    continue
                if not row or len(row) < 4:
                    continue

                time = clean_time(row[0] if len(row) > 0 else "")
                coach_name = str(row[1]).strip() if len(row) > 1 else ""
                group_name = str(row[2]).strip() if len(row) > 2 else ""
                kid_name = str(row[3]).strip() if len(row) > 3 else ""
                parent_email = str(row[8]).strip() if len(row) > 8 else ""

                # Skip empty/header rows
                if (
                    not time
                    or "time" in time.lower()
                    or not group_name
                    or group_name == "Group"
                ):
                    continue
                if not coach_name:
                    continue

                print(f"  {time} | {coach_name} | {group_name} | {kid_name}")

                # Get coach
                coach_id = get_coach_id(coach_name)
                if not coach_id:
                    print(f"    ⚠️ Coach '{coach_name}' not found!")
                    continue

                # Get/create group
                group_id = get_or_create_group(group_name, coach_id)

                # Add schedule
                add_schedule(group_id, day_num, time, coach_id)
                total_sessions += 1

                # Add enrollment if we have kid and parent info
                if kid_name and parent_email:
                    family_id = get_or_create_family(parent_email, kid_name)
                    if family_id:
                        add_enrollment(group_id, family_id, kid_name)
                        total_enrollments += 1

        except Exception as e:
            print(f"  ❌ Error reading {day_name}: {e}")

    print(f"\n✅ Sync complete!")
    print(f"   Sessions: {total_sessions}")
    print(f"   Enrollments: {total_enrollments}")


if __name__ == "__main__":
    sync()
