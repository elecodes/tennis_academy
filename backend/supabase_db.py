import os
import requests

SUPABASE_URL = os.environ.get(
    "SUPABASE_URL",
    "https://ypbwlpeighgpafocauzp.supabase.co/rest/v1",
)
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")


def _client():
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY or not SUPABASE_ANON_KEY:
        return None
    return {
        "url": SUPABASE_URL.rstrip("/"),
        "headers": {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Accept": "application/json",
        },
    }


def _fetch(table, order=None):
    client = _client()
    if not client:
        return None
    params = {}
    if order:
        params["order"] = order
    resp = requests.get(
        f"{client['url']}/{table}",
        headers=client["headers"],
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def fetch_students():
    return _fetch("students", order="name.asc")


def fetch_coaches():
    return _fetch("coaches", order="name.asc")


def fetch_lessons():
    return _fetch("lessons", order="day.asc,time.asc")


def fetch_seasons():
    return _fetch("seasons", order="name.asc")


def fetch_student_lessons():
    return _fetch("student_lessons")


def fetch_enrollments():
    students = _fetch("students")
    student_lessons = _fetch("student_lessons")
    lessons = _fetch("lessons")
    seasons = _fetch("seasons")
    coaches = _fetch("coaches")

    if not all([students, student_lessons, lessons, seasons, coaches]):
        return None

    season_map = {s["id"]: s["name"] for s in seasons}
    coach_map = {c["id"]: c["name"] for c in coaches}
    lesson_map = {l["id"]: l for l in lessons}

    sl_by_student = {}
    for sl in student_lessons:
        sl_by_student.setdefault(sl["student_id"], []).append(sl)

    enrollments = []
    for s in students:
        sid = s["id"]
        linked = sl_by_student.get(sid, [])
        parent_info = {
            "name": s.get("parent_name"),
            "email": s.get("parent_email"),
            "phone": s.get("parent_phone"),
        }

        season_name = season_map.get(s.get("season_id")) or str(s.get("season_id", ""))

        if not linked:
            enrollments.append({
                "student_name": s["name"],
                "parent": parent_info,
                "lesson_title": None,
                "lesson_day": s.get("day"),
                "lesson_time": None,
                "coach_name": None,
                "season_name": season_name,
                "status": s.get("status"),
                "payment_status": s.get("payment_status"),
                "price": s.get("price"),
                "welcome_kit": s.get("welcome_kit"),
            })
        else:
            for sl in linked:
                lesson = lesson_map.get(sl["lesson_id"], {})
                enrollments.append({
                    "student_name": s["name"],
                    "parent": parent_info,
                    "lesson_title": lesson.get("title"),
                    "lesson_day": lesson.get("day", s.get("day")),
                    "lesson_time": lesson.get("time"),
                    "coach_name": coach_map.get(lesson.get("coach_id")),
                    "season_name": season_name,
                    "status": s.get("status"),
                    "payment_status": s.get("payment_status"),
                    "price": s.get("price"),
                    "welcome_kit": s.get("welcome_kit"),
                })

    return enrollments
