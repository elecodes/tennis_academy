from pg_db import pg_query
from supabase_rest import get_table


def _rows_or_rest(rows, rest_fn):
    if rows is not None:
        return rows
    return rest_fn()


def fetch_students():
    return _rows_or_rest(
        pg_query("SELECT * FROM students ORDER BY name ASC"),
        lambda: get_table("students", order="name.asc"),
    )


def fetch_coaches():
    return _rows_or_rest(
        pg_query("SELECT * FROM coaches ORDER BY name ASC"),
        lambda: get_table("coaches", order="name.asc"),
    )


def fetch_lessons():
    return _rows_or_rest(
        pg_query("SELECT * FROM lessons ORDER BY day ASC, time ASC"),
        lambda: get_table("lessons", order="day.asc,time.asc"),
    )


def fetch_seasons():
    return _rows_or_rest(
        pg_query("SELECT * FROM seasons ORDER BY name ASC"),
        lambda: get_table("seasons", order="name.asc"),
    )


def fetch_student_lessons():
    return _rows_or_rest(
        pg_query("SELECT * FROM student_lessons"),
        lambda: get_table("student_lessons"),
    )


def fetch_enrollments():
    students = fetch_students()
    student_lessons = fetch_student_lessons()
    lessons = fetch_lessons()
    seasons = fetch_seasons()
    coaches = fetch_coaches()

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


def fetch_academy_users():
    coaches = fetch_coaches()
    students = fetch_students()

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
    coaches = fetch_coaches()
    lessons = fetch_lessons()
    students = fetch_students()
    student_lessons = fetch_student_lessons()

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


def fetch_coach_lessons(coach_name):
    coaches = fetch_coaches()
    lessons = fetch_lessons()
    student_lessons = fetch_student_lessons()

    if not all([coaches, lessons]):
        return None

    coach_ids = {c["id"] for c in coaches if c.get("name", "").lower() == coach_name.lower()}
    if not coach_ids:
        return []

    sl_by_lesson = {}
    for sl in (student_lessons or []):
        sl_by_lesson.setdefault(sl["lesson_id"], []).append(sl)

    DAY_MAP = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
               "friday": 4, "saturday": 5, "sunday": 6}

    seen = set()
    result = []
    for l in lessons:
        if l.get("coach_id") not in coach_ids:
            continue
        key = (l.get("day"), l.get("time"))
        if key in seen:
            continue
        seen.add(key)

        day_str = (l.get("day") or "").lower()
        day_num = DAY_MAP.get(day_str, 0)

        result.append({
            "id": l["id"],
            "title": l.get("title", "Lesson"),
            "day": day_num,
            "day_name": l.get("day", "").capitalize(),
            "time": (l.get("time") or "00:00:00")[:5],
            "type": l.get("type", "GROUP"),
            "student_count": len(sl_by_lesson.get(l["id"], [])),
        })

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    result.sort(key=lambda x: (x["day"], x["time"]))
    return result


def fetch_lesson_parents(lesson_id):
    students = fetch_students()
    student_lessons = fetch_student_lessons()

    if not all([students, student_lessons]):
        return None

    student_map = {s["id"]: s for s in students}

    parents = []
    seen_emails = set()
    for sl in student_lessons:
        if sl.get("lesson_id") != lesson_id:
            continue
        s = student_map.get(sl["student_id"])
        if not s:
            continue
        email = s.get("parent_email") or ""
        if not email or email in seen_emails:
            continue
        seen_emails.add(email)
        parents.append({
            "name": s.get("parent_name") or "Parent",
            "email": email,
            "phone": s.get("parent_phone") or "",
            "student_name": s.get("name", ""),
        })

    return parents


def fetch_timetable(role, user_name=None, user_email=None):
    lessons = fetch_lessons()
    coaches = fetch_coaches()
    students = fetch_students()
    student_lessons = fetch_student_lessons()

    if not all([lessons, coaches, students]):
        return None

    coach_map = {c["id"]: c for c in coaches}
    student_map = {s["id"]: s for s in students}

    sl_by_lesson = {}
    for sl in (student_lessons or []):
        sl_by_lesson.setdefault(sl["lesson_id"], []).append(sl)

    coach_ids = set()
    if role == "coach" and user_name:
        coach_ids = {c["id"] for c in coaches if c.get("name", "").lower() == user_name.lower()}

    family_lesson_ids = set()
    if role == "family" and user_email:
        family_students = [s for s in students if s.get("parent_email", "").lower() == user_email.lower()]
        family_student_ids = {s["id"] for s in family_students}
        for sl in (student_lessons or []):
            if sl["student_id"] in family_student_ids:
                family_lesson_ids.add(sl["lesson_id"])

    DAY_MAP = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6,
    }

    seen = {}
    groups = []
    for l in lessons:
        if role == "coach" and l["coach_id"] not in coach_ids:
            continue
        if role == "family" and l["id"] not in family_lesson_ids:
            continue

        coach = coach_map.get(l["coach_id"], {})
        coach_name = coach.get("name", "Unknown")

        day_str = l.get("day", "").lower()
        day_num = DAY_MAP.get(day_str, 0)

        start_time = l.get("time", "00:00:00")[:5]
        end_hour = int(l["time"][:2]) + 1 if l.get("time") else 1
        end_time = f"{end_hour:02d}:{l['time'][3:5]}" if l.get("time") else "01:00"

        dedup_key = (day_num, start_time, coach_name)
        if dedup_key in seen:
            existing = seen[dedup_key]
            for sl in sl_by_lesson.get(l["id"], []):
                s = student_map.get(sl["student_id"])
                if s and not any(k["name"] == s["name"] for k in existing["kids"]):
                    existing["kids"].append({"name": s["name"], "age": "Unknown"})
            continue

        lesson_students = []
        for sl in sl_by_lesson.get(l["id"], []):
            s = student_map.get(sl["student_id"])
            if s:
                lesson_students.append({"name": s["name"], "age": "Unknown"})

        group = {
            "id": l["id"],
            "name": l.get("title", "Lesson"),
            "schedule_text": f"{l.get('day', '').capitalize()} {start_time}",
            "level": l.get("type", "GROUP"),
            "coach": {
                "id": coach.get("id"),
                "name": coach_name,
                "email": coach.get("email"),
            },
            "kids": lesson_students,
            "schedules": [{
                "id": l["id"],
                "day": day_num,
                "start_time": start_time,
                "end_time": end_time,
                "court": l.get("notes", ""),
            }],
        }
        seen[dedup_key] = group
        groups.append(group)

    return {"groups": groups}


def fetch_family_enrollments(parent_email):
    students = fetch_students()
    student_lessons = fetch_student_lessons()
    lessons = fetch_lessons()
    coaches = fetch_coaches()

    if not all([students, student_lessons, lessons, coaches]):
        return None

    coach_map = {c["id"]: c["name"] for c in coaches}
    lesson_map = {l["id"]: l for l in lessons}

    DAYS = {
        "MONDAY": "Mon", "TUESDAY": "Tue", "WEDNESDAY": "Wed",
        "THURSDAY": "Thu", "FRIDAY": "Fri", "SATURDAY": "Sat", "SUNDAY": "Sun",
    }

    sl_by_student = {}
    for sl in student_lessons:
        sl_by_student.setdefault(sl["student_id"], []).append(sl)

    enrollments = []
    seen_lessons = set()
    for s in students:
        if s.get("parent_email", "").strip().lower() != parent_email.strip().lower():
            continue

        linked = sl_by_student.get(s["id"], [])
        if not linked:
            enrollments.append({
                "kid_name": s["name"],
                "name": "(no lesson assigned)",
                "coach_name": None,
            })
        else:
            for sl in linked:
                lesson = lesson_map.get(sl["lesson_id"], {})
                title = lesson.get("title", "")
                dedup_key = (s["name"], title)
                if dedup_key in seen_lessons:
                    continue
                seen_lessons.add(dedup_key)

                coach = coach_map.get(lesson.get("coach_id"), "")
                day_raw = (lesson.get("day") or "").upper()
                time_raw = lesson.get("time") or ""

                day_abbr = DAYS.get(day_raw, day_raw[:3].capitalize())
                hour = int(time_raw[:2]) if time_raw[:2].isdigit() else 0
                minute = time_raw[3:5] if len(time_raw) >= 5 else "00"
                ampm = "am" if hour < 12 else "pm"
                hour12 = hour if 1 <= hour <= 12 else (hour - 12 if hour > 12 else 12)
                time_str = f"{hour12}:{minute}{ampm}"

                enrollments.append({
                    "kid_name": s["name"],
                    "name": lesson.get("title", ""),
                    "coach_name": coach,
                    "schedule": f"{day_abbr} {time_str}",
                })

    return enrollments
