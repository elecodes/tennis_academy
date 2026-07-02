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


def fetch_supabase_users():
    coaches = _fetch("coaches", order="name.asc")
    students = _fetch("students", order="name.asc")

    if coaches is None or students is None:
        return None

    seen = set()
    users = []

    for c in coaches:
        key = c.get("email", "") or c.get("name", "")
        if key in seen:
            continue
        seen.add(key)
        users.append({
            "name": c.get("name", ""),
            "email": c.get("email", ""),
            "phone": c.get("phone", ""),
            "type": "Coach",
            "source": "Supabase",
            "status": "Active",
        })

    for s in students:
        key = s.get("parent_email", "") or s.get("name", "")
        if key in seen:
            continue
        seen.add(key)
        users.append({
            "name": s.get("name", ""),
            "email": s.get("parent_email", ""),
            "phone": s.get("parent_phone", ""),
            "type": "Student",
            "source": "Supabase",
            "status": (s.get("status") or "ACTIVE").capitalize(),
        })

    users.sort(key=lambda x: x["name"].lower())
    return users


def fetch_coach_groups(coach_name):
    coaches = _fetch("coaches")
    lessons = _fetch("lessons")
    students = _fetch("students")
    student_lessons = _fetch("student_lessons")

    if not all([coaches, lessons, students, student_lessons]):
        return None

    coach_ids = {c["id"] for c in coaches if c.get("name", "").lower() == coach_name.lower()}
    if not coach_ids:
        return []

    student_map = {s["id"]: s for s in students}

    sl_by_lesson = {}
    for sl in student_lessons:
        sl_by_lesson.setdefault(sl.get("lesson_id"), []).append(sl)

    seen_lessons = set()
    groups = []
    for l in lessons:
        if l.get("coach_id") not in coach_ids:
            continue
        key = (l.get("day"), l.get("time"))
        if key in seen_lessons:
            continue
        seen_lessons.add(key)

        lesson_students = []
        for sl in sl_by_lesson.get(l["id"], []):
            s = student_map.get(sl.get("student_id"))
            if s:
                lesson_students.append({
                    "name": s.get("name", ""),
                    "parent": s.get("parent_name", ""),
                })

        groups.append({
            "day": l.get("day", "").capitalize(),
            "time": l.get("time", ""),
            "title": l.get("title", ""),
            "students": lesson_students,
            "student_count": len(lesson_students),
        })

    DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    groups.sort(key=lambda g: (DAY_ORDER.index(g["day"]) if g["day"] in DAY_ORDER else 99, g["time"]))
    return groups
