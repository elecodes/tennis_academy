import os
import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SHEETS_WEBHOOK_URL = os.environ.get("GOOGLE_SHEETS_WEBHOOK_URL")


def sync_kid_update(
    original_kid_name,
    new_kid_name=None,
    parent_email=None,
    original_group_name=None,
    new_parent_email=None,
    new_group_name=None,
):
    if not GOOGLE_SHEETS_WEBHOOK_URL:
        print("Warning: GOOGLE_SHEETS_WEBHOOK_URL not set. Skipping sync.")
        return False

    payload = {
        "action": "update_kid",
        "originalKidName": original_kid_name,
        "newKidName": new_kid_name,
        "parentEmail": parent_email,
        "originalGroupName": original_group_name,
        "newParentEmail": new_parent_email,
        "newGroupName": new_group_name,
    }

    try:
        response = requests.post(GOOGLE_SHEETS_WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error syncing kid update to Google Sheets: {e}")
        return False


def sync_group_update(
    original_group_name,
    new_group_name=None,
    new_coach_name=None,
    new_schedule_time=None,
    day_of_week=None,
):
    if not GOOGLE_SHEETS_WEBHOOK_URL:
        print("Warning: GOOGLE_SHEETS_WEBHOOK_URL not set. Skipping sync.")
        return False

    payload = {
        "action": "update_group",
        "originalGroupName": original_group_name,
        "newGroupName": new_group_name,
        "newCoachName": new_coach_name,
        "newScheduleTime": new_schedule_time,
        "dayOfWeek": day_of_week,
    }

    try:
        response = requests.post(GOOGLE_SHEETS_WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error syncing group update to Google Sheets: {e}")
        return False
