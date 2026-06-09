"""
SF TENNIS KIDS Club - Communication System
A simple, free-tier communication platform for tennis clubs.
"""

import os
import sys

# Ensure backend submodules can be found when running from root or within backend/
sys.path.insert(0, os.path.dirname(__file__))

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    send_file,
    send_from_directory,
    make_response,
    jsonify,
)
import time
from functools import wraps
from datetime import datetime
from database import get_db, get_config, set_config
import sqlite3
from sync_webhook import sync_kid_update, sync_group_update
import requests
from migrate_schedules import parse_schedule

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables from .env if it exists
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

import warnings

warnings.filterwarnings(
    "ignore",
    message='Field name "schema" in .* shadows an attribute in parent "BaseModel"',
)

from services.ai.magic_draft import (
    generate_email_draft,
    AIDraftUnavailableError,
    AIDraftProviderError,
)

from routes.timetables import timetables_bp
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask_talisman import Talisman

if os.environ.get("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        send_default_pii=True,
    )

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static",
)
# Template caching: disable auto-reload in production for faster cold starts
is_production = (
    os.environ.get("FLASK_ENV") == "production" or os.environ.get("VERCEL") == "1"
)
app.jinja_env.auto_reload = not is_production
app.config["TEMPLATES_AUTO_RELOAD"] = not is_production
app.secret_key = os.environ.get(
    "SECRET_KEY", "7f0d44a016b40a094b21c5b7f45496cc78a65eeda08491094a17408b2c05c88d"
)


def format_schedule_compact(schedule_text):
    """
    Convert schedule text to compact mobile-friendly format.
    Handles: "Tue 4pm, Thu 4:30pm, Fri 3pm" -> ["Tue 4pm", "Thu 4:30pm", "Fri 3pm"]
    """
    if not schedule_text:
        return []

    import re

    days_map = {
        "mon": "Mon",
        "monday": "Mon",
        "tue": "Tue",
        "tuesday": "Tue",
        "tues": "Tue",
        "thur": "Thu",
        "thu": "Thu",
        "thursday": "Thu",
        "wed": "Wed",
        "wednesday": "Wed",
        "fri": "Fri",
        "friday": "Fri",
        "sat": "Sat",
        "saturday": "Sat",
        "sun": "Sun",
        "sunday": "Sun",
    }

    # Pattern to match "Day time" pairs - captures day and time together
    # Handles: "Mon 4pm", "Tue 4:30pm", "Mon 2:40pm"
    pair_pattern = (
        r"\b((?:mon|tue[sday]*|wednesday|thu(?:rsday)?|fri|sat(?:urday)?|sun(?:day)?))"
        r"\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\b"
    )

    matches = re.findall(pair_pattern, schedule_text, re.IGNORECASE)

    if matches:
        results = []
        for day_full, time_str in matches:
            day_lower = day_full.lower()[:3]
            day_short = days_map.get(day_lower, day_full.title()[:3])

            # Clean up time format
            time_str = time_str.strip()
            time_str = re.sub(r"\s+", "", time_str)  # Remove spaces

            results.append(f"{day_short} {time_str}")
        return results if results else [schedule_text]

    # Fallback: try to find just times
    time_pattern = r"(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)"
    times = re.findall(time_pattern, schedule_text, re.IGNORECASE)

    day_pattern = r"\b((?:mon|tue|weden|thu|fri|sat|sun)[a-z]*)\b"
    days = re.findall(day_pattern, schedule_text, re.IGNORECASE)

    if days and times:
        results = []
        day_short = days_map.get(days[0].lower()[:3], days[0].title()[:3])
        time_str = times[0].replace(" ", "")
        results.append(f"{day_short} {time_str}")
        return results

    return [schedule_text]


def format_time(time_str):
    """Convert time to clean 12h format (4pm, 9:30am)"""
    if not time_str:
        return ""
    try:
        time_str = time_str.strip().lower()
        # If already has am/pm, just clean it up
        if time_str.endswith("am") or time_str.endswith("pm"):
            suffix = "am" if time_str.endswith("am") else "pm"
            time_part = time_str[:-2].strip()
            parts = time_part.split(":")
            hour = int(parts[0])
            minute = parts[1] if len(parts) > 1 else "00"
            if minute == "00":
                return f"{hour}{suffix}"
            return f"{hour}:{minute}{suffix}"
        # Otherwise treat as 24-hour format
        parts = time_str.split(":")
        hour = int(parts[0])
        minute = parts[1] if len(parts) > 1 else "00"
        if hour == 0:
            return f"12:{minute}am"
        elif hour == 12:
            return f"12:{minute}pm"
        elif hour > 12:
            return f"{hour - 12}:{minute}pm"
        else:
            return f"{hour}:{minute}am" if minute != "00" else f"{hour}am"
    except Exception:
        return time_str


app.jinja_env.filters["schedule_compact"] = format_schedule_compact
app.jinja_env.filters["format_time"] = format_time


def cache_response(max_age=300):
    """Add Cache-Control headers to GET responses.

    Uses 'private' so each browser caches separately (respects RBAC).
    Only active in production (not debug mode).

    If a sync happened within the last 60 seconds, reduces max-age to 30
    so users see fresh data sooner after spreadsheet updates.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            resp = f(*args, **kwargs)
            if not app.debug and request.method == "GET":
                resp = make_response(resp)
                try:
                    last_sync = int(get_config("last_sync_at") or "0")
                    elapsed = time.time() - last_sync
                    effective_max = 30 if elapsed < 60 else max_age
                except Exception:
                    effective_max = max_age
                resp.headers["Cache-Control"] = f"private, max-age={effective_max}"
            return resp

        return wrapper

    return decorator


# Security Headers (Talisman)
csp = {
    "default-src": "'self'",
    "script-src": [
        "'self'",
        "'unsafe-inline'",  # Required for Tailwind CDN and some templates
        "cdn.tailwindcss.com",
        "browser.sentry-cdn.com",
    ],
    "style-src": [
        "'self'",
        "'unsafe-inline'",  # Required for Tailwind CDN and internal styles
        "fonts.googleapis.com",
    ],
    "font-src": [
        "'self'",
        "fonts.gstatic.com",
    ],
    "img-src": [
        "'self'",
        "data:",
    ],
    "connect-src": [
        "'self'",
        "*.ingest.sentry.io",
    ],
}

Talisman(
    app,
    content_security_policy=csp,
    force_https=False,
    frame_options="DENY",
)

app.register_blueprint(timetables_bp)


# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "academy.db")

# Email configuration - Using Gmail SMTP (free)
# Set TEST_MODE = False to send emails to real family addresses.
TEST_MODE = True  # Set to False in production
REDIRECT_TARGET = "gelenmp@gmail.com"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "gelenmp@gmail.com")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "zqjl piud eqwi guci")
REDIRECT_EMAILS_TO = REDIRECT_TARGET if TEST_MODE else None


def init_db():
    """Initialize the database with tables (Local or Cloud)."""
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'coach', 'family')),
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """
    )

    # Groups table (tennis groups like "Beginners Mon/Wed", "Advanced Tue/Thu")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            schedule TEXT NOT NULL,
            coach_id INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (coach_id) REFERENCES users (id) ON DELETE SET NULL
        )
    """
    )

    # Group memberships (families enrolled in groups)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            family_id INTEGER NOT NULL,
            kid_name TEXT NOT NULL,
            schedule_id INTEGER,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
            FOREIGN KEY (family_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (schedule_id) REFERENCES group_schedules (id) ON DELETE SET NULL,
            UNIQUE(group_id, family_id, kid_name, schedule_id)
        )
    """
    )

    # Add schedule_id column if it doesn't exist (for existing databases)
    cursor.execute("PRAGMA table_info(group_members)")
    columns = [col[1] for col in cursor.fetchall()]
    if "schedule_id" not in columns:
        cursor.execute(
            "ALTER TABLE group_members ADD COLUMN schedule_id INTEGER REFERENCES group_schedules(id) ON DELETE SET NULL"
        )

    # Messages table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            group_id INTEGER,
            message_type TEXT NOT NULL CHECK(
                message_type IN (
                    'rain_cancellation', 'coach_delay', 'announcement', 'schedule_change'
                )
            ),
            subject TEXT NOT NULL,
            content TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_general INTEGER DEFAULT 0,
            FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE SET NULL
        )
    """
    )

    # Message recipients (tracking who received what)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS message_recipients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            email_sent INTEGER DEFAULT 0,
            sent_at TIMESTAMP,
            FOREIGN KEY (message_id) REFERENCES messages (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """
    )

    # Group schedules table
    cursor.execute(
        """
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
    """
    )

    # App config (key-value store for sync metadata, cache versions, etc.)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS app_config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()

    # Initialize app_config defaults
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO app_config (key, value) VALUES ('last_sync_at', '0')"
    )
    conn.commit()
    conn.close()


def send_email(to_email, subject, body):
    """Send email using SMTP."""
    if REDIRECT_EMAILS_TO:
        body = f"--- [TEST MODE] REDIRECTED FROM: {to_email} ---\n\n" + body
        to_email = REDIRECT_EMAILS_TO

    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"CRITICAL: Email delivery failed to {to_email}. Error: {e}")
        return False


# Decorators for role-based access
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)

    return decorated_function


def coach_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session or session.get("role") not in ["admin", "coach"]:
            flash("Coach access required.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)

    return decorated_function


# Routes
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/manifest.json")
def manifest():
    try:
        # Use an absolute path that works both locally and on Vercel
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "..", "frontend", "static", "manifest.json")
        return send_file(path)
    except Exception:
        return send_from_directory(app.static_folder, "manifest.json")


@app.route("/sw.js")
def sw():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "..", "frontend", "static", "sw.js")
        response = make_response(send_file(path))
        response.headers["Content-Type"] = "application/javascript"
        return response
    except Exception:
        response = make_response(send_from_directory(app.static_folder, "sw.js"))
        response.headers["Content-Type"] = "application/javascript"
        return response


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.static_folder, "icons"), "icon-192.png")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("login.html")

        conn = get_db()
        # Fetch all matching active users (could be multiple with same email now)
        users = conn.execute(
            "SELECT * FROM users WHERE email = ? AND is_active = 1", (email,)
        ).fetchall()
        conn.close()

        found_user = None
        for user in users:
            if check_password_hash(user["password"], password):
                found_user = user
                break

        if found_user:
            session["user_id"] = found_user["id"]
            session["email"] = found_user["email"]
            session["role"] = found_user["role"]
            session["full_name"] = found_user["full_name"]
            flash(f"Welcome, {found_user['full_name']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
@cache_response(max_age=120)
def dashboard():
    conn = get_db()
    user_id = session["user_id"]
    role = session["role"]

    if role == "admin":
        # Admin sees everything
        stats = {
            "total_users": conn.execute(
                "SELECT COUNT(*) FROM users WHERE role != 'admin'"
            ).fetchone()[0],
            "total_groups": conn.execute("SELECT COUNT(*) FROM groups").fetchone()[0],
            "total_messages": conn.execute("SELECT COUNT(*) FROM messages").fetchone()[
                0
            ],
            "recent_messages": conn.execute(
                """
                SELECT m.*, u.full_name as sender_name, g.name as group_name
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                LEFT JOIN groups g ON m.group_id = g.id
                ORDER BY m.sent_at DESC LIMIT 5
            """
            ).fetchall(),
        }
        template = "admin_dashboard.html"

    elif role == "coach":
        # Coach sees their groups and messages
        my_groups = conn.execute(
            """
            SELECT g.*, COUNT(DISTINCT gm.family_id) as member_count
            FROM groups g
            LEFT JOIN group_members gm ON g.id = gm.group_id
            WHERE g.coach_id = ?
            GROUP BY g.id
        """,
            (user_id,),
        ).fetchall()

        recent_messages = conn.execute(
            """
            SELECT DISTINCT m.*, u.full_name as sender_name, g.name as group_name
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            LEFT JOIN groups g ON m.group_id = g.id
            LEFT JOIN message_recipients mr ON m.id = mr.message_id
            WHERE m.sender_id = ?
               OR m.group_id IN (SELECT id FROM groups WHERE coach_id = ?)
               OR mr.user_id = ?
               OR m.is_general = 1
            ORDER BY m.sent_at DESC LIMIT 10
        """,
            (user_id, user_id, user_id),
        ).fetchall()

        total_families = sum(group["member_count"] for group in my_groups)

        total_sessions = conn.execute(
            """
            SELECT COUNT(*) FROM group_schedules gs
            JOIN groups g ON gs.group_id = g.id
            WHERE g.coach_id = ?
        """,
            (user_id,),
        ).fetchone()[0]

        stats = {
            "my_groups": my_groups,
            "recent_messages": recent_messages,
            "total_families": total_families,
            "total_sessions": total_sessions,
        }
        template = "coach_dashboard.html"

    else:  # family
        # Family sees their enrolled groups and messages
        my_enrollments = conn.execute(
            """
            SELECT g.*, gm.kid_name, u.full_name as coach_name
            FROM group_members gm
            JOIN groups g ON gm.group_id = g.id
            LEFT JOIN users u ON g.coach_id = u.id
            WHERE gm.family_id = ?
        """,
            (user_id,),
        ).fetchall()

        messages = conn.execute(
            """
            SELECT DISTINCT m.*, u.full_name as sender_name, g.name as group_name
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            LEFT JOIN groups g ON m.group_id = g.id
            LEFT JOIN message_recipients mr ON m.id = mr.message_id
            WHERE m.group_id IN (SELECT group_id FROM group_members WHERE family_id = ?)
               OR mr.user_id = ?
               OR m.is_general = 1
            ORDER BY m.sent_at DESC
        """,
            (user_id, user_id),
        ).fetchall()

        stats = {"my_enrollments": my_enrollments, "messages": messages}
        template = "family_dashboard.html"

    conn.close()
    return render_template(template, stats=stats)


# ==================== ADMIN ROUTES ====================


@app.route("/admin/users")
@admin_required
@cache_response(max_age=300)
def admin_users():
    conn = get_db()
    users = conn.execute(
        """
        SELECT u.*,
               (SELECT COUNT(*) FROM group_members WHERE family_id = u.id) as enrollments
        FROM users u
        ORDER BY u.created_at DESC
    """
    ).fetchall()
    conn.close()
    return render_template("admin/users.html", users=users)


@app.route("/admin/users/add", methods=["POST"])
@admin_required
def admin_add_user():
    email = request.form.get("email", "").strip().lower()
    full_name = request.form.get("full_name", "").strip()
    role = request.form.get("role", "family")
    phone = request.form.get("phone", "").strip()
    password = request.form.get("password", "")

    # Validation
    if (
        not email
        or not full_name
        or not password
        or role not in ["admin", "coach", "family"]
    ):
        flash(
            "All fields are required and role must be admin, coach or family.", "danger"
        )
        return redirect(url_for("admin_users"))

    if len(password) < 6:
        flash("Password must be at least 6 characters.", "danger")
        return redirect(url_for("admin_users"))

    conn = get_db()
    try:
        hashed_password = generate_password_hash(password)
        conn.execute(
            """
            INSERT INTO users (email, password, full_name, role, phone)
            VALUES (?, ?, ?, ?, ?)
        """,
            (email, hashed_password, full_name, role, phone),
        )
        conn.commit()
        flash(f"User {full_name} added successfully!", "success")
    except sqlite3.IntegrityError:
        flash("Email already exists.", "danger")
    return redirect(url_for("admin_users"))


@app.route("/admin/users/edit", methods=["POST"])
@admin_required
def admin_edit_user():
    user_id = request.form.get("user_id")
    email = request.form.get("email", "").strip().lower()
    full_name = request.form.get("full_name", "").strip()
    role = request.form.get("role", "family")
    phone = request.form.get("phone", "").strip()

    if not all([user_id, email, full_name]) or role not in ["coach", "family"]:
        flash("Email, name and valid role are required.", "danger")
        return redirect(url_for("admin_users"))

    conn = get_db()
    try:
        # Get old info for webhook
        old_user = conn.execute(
            "SELECT full_name, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()

        conn.execute(
            """
            UPDATE users
            SET email = ?, full_name = ?, role = ?, phone = ?
            WHERE id = ?
        """,
            (email, full_name, role, phone, user_id),
        )
        conn.commit()

        if old_user and role == "family":
            # Just push the user update, Google Sheets will find the kidName and update the email if present
            # We don't have the kidName here, just the family full_name and email
            # This is tricky because the spreadsheet is kid-centric.
            # If the family email changes, we need to update all kids for this family.
            kids = conn.execute(
                "SELECT kid_name, g.name FROM group_members gm JOIN groups g ON gm.group_id = g.id WHERE family_id = ?",
                (user_id,),
            ).fetchall()
            for kid in kids:
                sync_kid_update(
                    original_kid_name=kid["kid_name"],
                    parent_email=old_user["email"],
                    new_parent_email=email,
                )

        flash(f"User {full_name} updated successfully!", "success")
    except sqlite3.IntegrityError:
        flash("Email already exists.", "danger")
    finally:
        conn.close()

    return redirect(url_for("admin_users"))


@app.route("/admin/users/delete/<int:user_id>", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    if user_id == session.get("user_id"):
        flash("You cannot delete your own administrative account.", "danger")
        return redirect(url_for("admin_users"))

    conn = get_db()
    try:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        flash("User deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting user: {e}", "danger")
    finally:
        conn.close()

    return redirect(url_for("admin_users"))


@app.route("/admin/groups")
@admin_required
@cache_response(max_age=300)
def admin_groups():
    conn = get_db()
    groups = conn.execute(
        """
        SELECT g.id, g.name, g.coach_id, g.description, g.created_at,
               g.schedule,
               u.full_name as coach_name,
               COUNT(DISTINCT gm.family_id) as member_count
        FROM groups g
        LEFT JOIN users u ON g.coach_id = u.id
        LEFT JOIN group_members gm ON g.id = gm.group_id
        GROUP BY g.id
        ORDER BY g.created_at DESC
    """
    ).fetchall()
    coaches = conn.execute(
        "SELECT id, full_name FROM users WHERE role = 'coach' ORDER BY full_name"
    ).fetchall()
    conn.close()
    return render_template("admin/groups.html", groups=groups, coaches=coaches)


@app.route("/admin/groups/add", methods=["POST"])
@admin_required
def admin_add_group():
    name = request.form.get("name", "").strip()
    schedule = request.form.get("schedule", "").strip()
    coach_id = request.form.get("coach_id")
    description = request.form.get("description", "").strip()

    # Validation
    if not name or not schedule:
        flash("Group name and schedule are required.", "danger")
        return redirect(url_for("admin_groups"))

    if coach_id and coach_id.strip() == "":
        coach_id = None
    else:
        coach_id = int(coach_id) if coach_id else None

    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO groups (name, schedule, coach_id, description)
            VALUES (?, ?, ?, ?)
        """,
            (name, schedule, coach_id, description),
        )
        conn.commit()
        flash(f'Group "{name}" created successfully!', "success")
    except sqlite3.IntegrityError:
        flash("A group with this name already exists.", "danger")
    finally:
        conn.close()

    return redirect(url_for("admin_groups"))


@app.route("/admin/groups/edit", methods=["POST"])
@admin_required
def admin_edit_group():
    group_id = request.form.get("group_id")
    name = request.form.get("name", "").strip()
    schedule = request.form.get("schedule", "").strip()
    coach_id = request.form.get("coach_id")
    description = request.form.get("description", "").strip()

    if not all([group_id, name, schedule]):
        flash("Group name and schedule are required.", "danger")
        return redirect(url_for("admin_groups"))

    if coach_id and coach_id.strip() == "":
        coach_id = None
    else:
        coach_id = int(coach_id) if coach_id else None

    conn = get_db()
    try:
        # Get old info for webhook
        old_group = conn.execute(
            """
            SELECT g.name, u.full_name as coach_name
            FROM groups g
            LEFT JOIN users u ON g.coach_id = u.id
            WHERE g.id = ?
            """,
            (group_id,),
        ).fetchone()

        conn.execute(
            """
            UPDATE groups
            SET name = ?, schedule = ?, coach_id = ?, description = ?
            WHERE id = ?
        """,
            (name, schedule, coach_id, description, group_id),
        )
        conn.commit()

        if old_group:
            # Current coach name for the webhook (newly selected)
            new_coach_name = None
            if coach_id:
                coach = conn.execute(
                    "SELECT full_name FROM users WHERE id = ?", (coach_id,)
                ).fetchone()
                if coach:
                    new_coach_name = coach["full_name"]

            sync_group_update(
                original_group_name=old_group["name"],
                original_coach_name=old_group["coach_name"],
                new_group_name=name,
                new_coach_name=new_coach_name,
            )

        msg = (
            f'Group "{name}" updated successfully! Note: Timetable sessions are NOT automatically updated. '
            f'Use "Repair Timetable" if needed.'
        )
        flash(msg, "success")
    except sqlite3.IntegrityError:
        flash("A group with this name already exists.", "danger")
    finally:
        conn.close()

    return redirect(url_for("admin_groups"))


@app.route("/admin/sync-spreadsheet", methods=["POST"])
@admin_required
def admin_sync_spreadsheet():
    """Trigger a full sync from Google Sheets via the Apps Script."""
    webhook_url = os.environ.get("GOOGLE_SHEETS_WEBHOOK_URL")
    if not webhook_url:
        flash("Google Sheets webhook URL not configured.", "danger")
        return redirect(url_for("admin_groups"))

    try:
        response = requests.post(
            webhook_url,
            json={"action": "sync_all"},
            timeout=120,
        )
        if response.status_code == 200:
            res_data = response.json()
            version = res_data.get("version", "LEGACY")
            flash(
                f"Sync successful! {res_data.get('rows_processed', 0)} rows processed (Script: {version}).",
                "success",
            )
        else:
            flash(f"Sync failed: {response.text}", "danger")
    except Exception as e:
        flash(f"Error triggering sync: {e}", "danger")

    return redirect(url_for("admin_groups"))


@app.route("/api/webhook/sheets-sync", methods=["POST"])
def sheets_sync_webhook():
    """Receive sync notifications from Google Apps Script.

    Called automatically by GAS onEdit trigger and hourly timer.
    GAS already writes to Turso directly — this endpoint just
    records the sync timestamp for adaptive cache invalidation.
    """
    sync_key = os.environ.get("SYNC_API_KEY")
    if not sync_key:
        return jsonify({"status": "error", "message": "Server not configured"}), 500

    if request.headers.get("X-Sync-Key") != sync_key:
        return jsonify({"status": "error", "message": "Invalid sync key"}), 401

    data = request.get_json(silent=True) or {}
    action = data.get("action")

    if action in ("sync_all", "sync_row"):
        set_config("last_sync_at", str(int(time.time())))
        return jsonify(
            {
                "status": "ok",
                "rows_processed": data.get("rows_processed", 0),
            }
        )

    return jsonify({"status": "error", "message": f"Unknown action: {action}"}), 400


@app.route("/admin/repair-timetable", methods=["POST"])
@admin_required
def admin_repair_timetable():
    """Repopulate group_schedules from the text-based schedules in groups table."""
    conn = get_db()
    try:
        # Get all groups
        groups = conn.execute("SELECT id, name, schedule FROM groups").fetchall()

        repaired = 0
        for group in groups:
            schedules = parse_schedule(group["schedule"])
            if not schedules:
                continue

            # Clear existing structured schedules for this group
            # First, clear schedule_id references to avoid FK constraint
            conn.execute(
                "UPDATE group_members SET schedule_id = NULL"
                " WHERE group_id = ? AND schedule_id IN"
                " (SELECT id FROM group_schedules WHERE group_id = ?)",
                (group["id"], group["id"]),
            )
            conn.execute(
                "DELETE FROM group_schedules WHERE group_id = ?", (group["id"],)
            )

            for s in schedules:
                conn.execute(
                    """
                    INSERT INTO group_schedules (group_id, day_of_week, start_time, end_time, court)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (group["id"], s["day"], s["start"], s["end"], s["court"]),
                )
            repaired += 1

        conn.commit()
        flash(f"Timetable repaired for {repaired} groups.", "success")
    except Exception as e:
        flash(f"Error repairing timetable: {e}", "danger")
    finally:
        conn.close()

    return redirect(url_for("admin_groups"))


@app.route("/admin/groups/delete/<int:group_id>", methods=["POST"])
@admin_required
def admin_delete_group(group_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM groups WHERE id = ?", (group_id,))
        conn.commit()
        flash("Group deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting group: {e}", "danger")
    finally:
        conn.close()

    return redirect(url_for("admin_groups"))


@app.route("/admin/enrollments")
@admin_required
@cache_response(max_age=300)
def admin_enrollments():
    conn = get_db()
    enrollments = conn.execute(
        """
        SELECT gm.*, g.name as group_name, u.full_name as family_name, u.email
        FROM group_members gm
        JOIN groups g ON gm.group_id = g.id
        JOIN users u ON gm.family_id = u.id
        ORDER BY g.name, u.full_name
    """
    ).fetchall()
    groups = conn.execute("SELECT id, name FROM groups ORDER BY name").fetchall()
    families = conn.execute(
        "SELECT id, full_name, email FROM users WHERE role = 'family' ORDER BY full_name"
    ).fetchall()
    conn.close()
    return render_template(
        "admin/enrollments.html",
        enrollments=enrollments,
        groups=groups,
        families=families,
    )


@app.route("/admin/enrollments/add", methods=["POST"])
@admin_required
def admin_add_enrollment():
    group_id = request.form.get("group_id")
    family_id = request.form.get("family_id")
    kid_name = request.form.get("kid_name", "").strip()

    # Validation
    if not group_id or not family_id or not kid_name:
        flash("All fields are required.", "danger")
        return redirect(url_for("admin_enrollments"))

    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO group_members (group_id, family_id, kid_name)
            VALUES (?, ?, ?)
        """,
            (int(group_id), int(family_id), kid_name),
        )
        conn.commit()
        flash(f"{kid_name} enrolled successfully!", "success")
    except sqlite3.IntegrityError:
        flash("This kid is already enrolled in this group.", "danger")
    except ValueError:
        flash("Invalid group or family selected.", "danger")
    finally:
        conn.close()

    return redirect(url_for("admin_enrollments"))


@app.route("/admin/enrollments/edit", methods=["POST"])
@admin_required
def admin_edit_enrollment():
    enrollment_id = request.form.get("enrollment_id")
    group_id = request.form.get("group_id")
    family_id = request.form.get("family_id")
    kid_name = request.form.get("kid_name", "").strip()

    if not all([enrollment_id, group_id, family_id, kid_name]):
        flash("All fields are required.", "danger")
        return redirect(url_for("admin_enrollments"))

    conn = get_db()
    try:
        # Get old info for webhook
        old_enrollment = conn.execute(
            """
            SELECT kid_name, g.name as group_name, u.email as parent_email
            FROM group_members gm
            JOIN groups g ON gm.group_id = g.id
            JOIN users u ON gm.family_id = u.id
            WHERE gm.id = ?
            """,
            (enrollment_id,),
        ).fetchone()

        conn.execute(
            """
            UPDATE group_members
            SET group_id = ?, family_id = ?, kid_name = ?
            WHERE id = ?
        """,
            (int(group_id), int(family_id), kid_name, enrollment_id),
        )
        conn.commit()

        if old_enrollment:
            # We also need the new group name and parent email if those changed
            new_info = conn.execute(
                """
                SELECT g.name as group_name, u.email as parent_email
                FROM groups g, users u
                WHERE g.id = ? AND u.id = ?
                """,
                (int(group_id), int(family_id)),
            ).fetchone()

            if new_info:
                sync_kid_update(
                    original_kid_name=old_enrollment["kid_name"],
                    new_kid_name=kid_name,
                    parent_email=old_enrollment["parent_email"],
                    original_group_name=old_enrollment["group_name"],
                    new_parent_email=new_info["parent_email"],
                    new_group_name=new_info["group_name"],
                )

        flash(f"Enrollment for {kid_name} updated successfully!", "success")
    except sqlite3.IntegrityError:
        flash("This kid is already enrolled in this group.", "danger")
    finally:
        conn.close()

    return redirect(url_for("admin_enrollments"))


@app.route("/admin/enrollments/delete/<int:enrollment_id>", methods=["POST"])
@admin_required
def admin_delete_enrollment(enrollment_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM group_members WHERE id = ?", (enrollment_id,))
        conn.commit()
        flash("Enrollment removed successfully!", "success")
    except Exception as e:
        flash(f"Error removing enrollment: {e}", "danger")
    finally:
        conn.close()

    return redirect(url_for("admin_enrollments"))


@app.route("/api/draft-message", methods=["POST"])
@app.route("/admin/api/draft-message", methods=["POST"])
@coach_required
def api_draft_message():
    try:
        data = request.get_json()
        if not data:
            return {"error": "Invalid JSON"}, 400

        message_type = data.get("message_type", "general_update")
        notes = data.get("notes", "")

        if not notes:
            return {"error": "Notes are required"}, 400

        # Call the refactored AI service
        result = generate_email_draft(message_type, notes)
        return result
    except AIDraftUnavailableError as e:
        app.logger.warning(f"AI draft unavailable: {e}")
        return {"error": str(e)}, 503
    except AIDraftProviderError as e:
        app.logger.error(f"AI provider error while drafting message: {e}")
        return {"error": "AI service temporarily unavailable. Please try again."}, 502
    except Exception as e:
        app.logger.error(f"Error drafting message: {e}")
        return {"error": "An internal error occurred"}, 500


@app.route("/admin/send-message", methods=["GET", "POST"])
@admin_required
def admin_send_message():
    conn = get_db()
    try:
        if request.method == "POST":
            message_type = request.form.get("message_type")
            subject = request.form.get("subject", "").strip()
            content = request.form.get("content", "").strip()
            group_id = request.form.get("group_id")
            schedule_id = request.form.get("schedule_id")
            is_general = 1 if request.form.get("is_general") else 0

            # Validation
            if not message_type or not subject or not content:
                flash("Message type, subject, and content are required.", "danger")
                groups = conn.execute(
                    "SELECT id, name FROM groups ORDER BY name"
                ).fetchall()
                return render_template("admin/send_message.html", groups=groups)

            # Insert message
            cursor = conn.execute(
                """
                INSERT INTO messages (sender_id, group_id, message_type, subject, content, is_general)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    session["user_id"],
                    group_id if group_id else None,
                    message_type,
                    subject,
                    content,
                    is_general,
                ),
            )
            message_id = cursor.lastrowid

            # Determine recipients
            if is_general or not group_id:
                recipients = conn.execute(
                    "SELECT id, email FROM users WHERE role = 'family' AND is_active = 1"
                ).fetchall()
                is_general = 1  # Force general if group_id is missing
            else:
                # Filter by specific schedule slot if provided
                if schedule_id:
                    recipients = conn.execute(
                        """
                        SELECT DISTINCT u.id, u.email FROM users u
                        JOIN group_members gm ON u.id = gm.family_id
                        WHERE gm.group_id = ? AND gm.schedule_id = ? AND u.is_active = 1
                    """,
                        (group_id, schedule_id),
                    ).fetchall()
                else:
                    recipients = conn.execute(
                        """
                        SELECT DISTINCT u.id, u.email FROM users u
                        JOIN group_members gm ON u.id = gm.family_id
                        WHERE gm.group_id = ? AND u.is_active = 1
                    """,
                        (group_id,),
                    ).fetchall()

            if not recipients:
                flash(
                    "No active recipients found for the selected audience.", "warning"
                )
                groups = conn.execute(
                    "SELECT id, name FROM groups ORDER BY name"
                ).fetchall()
                return render_template("admin/send_message.html", groups=groups)

            # Send emails and track
            email_body = f"""
SF TENNIS KIDS Club Notification

Type: {message_type.replace("_", " ").title()}
Subject: {subject}

{content}

---
This message was sent from the SF TENNIS KIDS Club Communication System.
            """

            sent_count = 0
            failed_emails = []
            for recipient in recipients:
                if send_email(
                    recipient["email"], f"[SF TENNIS KIDS Club] {subject}", email_body
                ):
                    conn.execute(
                        """
                        INSERT INTO message_recipients (message_id, user_id, email_sent, sent_at)
                        VALUES (?, ?, 1, CURRENT_TIMESTAMP)
                    """,
                        (message_id, recipient["id"]),
                    )
                    sent_count += 1
                else:
                    conn.execute(
                        """
                        INSERT INTO message_recipients (message_id, user_id, email_sent)
                        VALUES (?, ?, 0)
                    """,
                        (message_id, recipient["id"]),
                    )
                    failed_emails.append(recipient["email"])

            conn.commit()

            if sent_count > 0:
                msg = f"Broadcast sent to {sent_count} recipients!"
                if failed_emails:
                    msg += f" Failed to reach: {', '.join(failed_emails)}"
                flash(msg, "success" if not failed_emails else "warning")
            else:
                flash(
                    "Failed to send broadcast to any recipients. Check SMTP settings.",
                    "danger",
                )

            return redirect(url_for("dashboard"))

        # Fetch groups with their schedules for the dropdown
        groups = conn.execute(
            """
            SELECT g.id as group_id, g.name as group_name,
                   gs.id as schedule_id, gs.day_of_week, gs.start_time, gs.end_time, gs.court
            FROM groups g
            LEFT JOIN group_schedules gs ON g.id = gs.group_id
            ORDER BY g.name, gs.day_of_week, gs.start_time
            """
        ).fetchall()
        return render_template("admin/send_message.html", groups=groups)

    except Exception as e:
        print(f"CRITICAL ERROR in admin_send_message: {e}")
        flash(f"An error occurred while sending the broadcast: {e}", "danger")
        return redirect(url_for("dashboard"))
    finally:
        conn.close()


@app.route("/admin/test-email", methods=["POST"])
@admin_required
def admin_test_email():
    """Send a test email to verify SMTP configuration."""
    test_recipient = request.form.get("test_email", "").strip()
    if not test_recipient:
        flash("Please provide a test email address.", "warning")
        return redirect(url_for("dashboard"))

    subject = "SF TENNIS KIDS Club - Test Connection"
    body = f"This is a test email sent at {datetime.now()} to verify your SMTP settings are working correctly."

    success = False
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = test_recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        success = True
    except Exception as e:
        flash(f"SMTP Error: {str(e)}", "danger")
        print(f"Test Email Error: {e}")

    if success:
        flash(f"Test email successfully sent to {test_recipient}!", "success")

    return redirect(url_for("dashboard"))


@app.route("/admin/messages/delete/<int:message_id>", methods=["POST"])
@admin_required
def admin_delete_message(message_id):
    conn = get_db()
    try:
        # recipients will be deleted automatically due to ON DELETE CASCADE
        conn.execute("DELETE FROM messages WHERE id = ?", (message_id,))
        conn.commit()
        flash("Communication log entry deleted.", "success")
    except Exception as e:
        flash(f"Error deleting message: {e}", "danger")
    finally:
        conn.close()

    return redirect(url_for("dashboard"))


# ==================== COACH ROUTES ====================


@app.route("/coach/send-message", methods=["GET", "POST"])
@coach_required
def coach_send_message():
    conn = get_db()
    coach_id = session["user_id"]

    try:
        my_groups = conn.execute(
            """
            SELECT g.id as group_id, g.name as group_name, g.schedule,
                   gs.id as schedule_id, gs.day_of_week, gs.start_time, gs.end_time, gs.court
            FROM groups g
            LEFT JOIN group_schedules gs ON g.id = gs.group_id
            WHERE g.coach_id = ?
            ORDER BY g.name, gs.day_of_week, gs.start_time
            """,
            (coach_id,),
        ).fetchall()

        if request.method == "POST":
            message_type = request.form.get("message_type")
            subject = request.form.get("subject", "").strip()
            content = request.form.get("content", "").strip()
            group_id = request.form.get("group_id")
            schedule_id = request.form.get("schedule_id")

            # Validation
            if not message_type or not subject or not content or not group_id:
                flash("All fields are required.", "danger")
                return render_template("coach/send_message.html", groups=my_groups)

            # Verify this group belongs to the coach
            group = conn.execute(
                "SELECT id, name FROM groups WHERE id = ? AND coach_id = ?",
                (group_id, coach_id),
            ).fetchone()
            if not group:
                flash("Invalid group selected.", "danger")
                return redirect(url_for("coach_send_message"))

            # Insert message
            cursor = conn.execute(
                """
                INSERT INTO messages (sender_id, group_id, message_type, subject, content, is_general)
                VALUES (?, ?, ?, ?, ?, 0)
            """,
                (coach_id, group_id, message_type, subject, content),
            )
            message_id = cursor.lastrowid

            # Get recipients - filter by specific schedule slot if provided
            if schedule_id:
                recipients = conn.execute(
                    """
                    SELECT DISTINCT u.id, u.email FROM users u
                    JOIN group_members gm ON u.id = gm.family_id
                    WHERE gm.group_id = ? AND gm.schedule_id = ? AND u.is_active = 1
                """,
                    (group_id, schedule_id),
                ).fetchall()
            else:
                recipients = conn.execute(
                    """
                    SELECT DISTINCT u.id, u.email FROM users u
                    JOIN group_members gm ON u.id = gm.family_id
                    WHERE gm.group_id = ? AND u.is_active = 1
                """,
                    (group_id,),
                ).fetchall()

            # Send emails
            email_body = f"""
SF TENNIS KIDS Club Notification - From Coach {session["full_name"]}

Type: {message_type.replace("_", " ").title()}
Group: {group["name"]}
Subject: {subject}

{content}

---
This message was sent from the SF TENNIS KIDS Club Communication System.
            """

            sent_count = 0
            failed_emails = []
            for recipient in recipients:
                if send_email(
                    recipient["email"], f"[SF TENNIS KIDS Club] {subject}", email_body
                ):
                    conn.execute(
                        """
                        INSERT INTO message_recipients (message_id, user_id, email_sent, sent_at)
                        VALUES (?, ?, 1, CURRENT_TIMESTAMP)
                    """,
                        (message_id, recipient["id"]),
                    )
                    sent_count += 1
                else:
                    conn.execute(
                        """
                        INSERT INTO message_recipients (message_id, user_id, email_sent)
                        VALUES (?, ?, 0)
                    """,
                        (message_id, recipient["id"]),
                    )
                    failed_emails.append(recipient["email"])

            conn.commit()

            if sent_count > 0:
                msg = f"Message sent to {sent_count} families!"
                if failed_emails:
                    msg += f" Failed to reach: {', '.join(failed_emails)}"
                flash(msg, "success" if not failed_emails else "warning")
            else:
                flash(
                    "Failed to send message to any families. Check SMTP settings.",
                    "danger",
                )

            return redirect(url_for("dashboard"))

        return render_template("coach/send_message.html", groups=my_groups)

    except Exception as e:
        print(f"CRITICAL ERROR in coach_send_message: {e}")
        flash(f"An error occurred while sending the message: {e}", "danger")
        return redirect(url_for("dashboard"))
    finally:
        conn.close()


@app.route("/coach/my-groups")
@coach_required
@cache_response(max_age=300)
def coach_my_groups():
    conn = get_db()
    coach_id = session["user_id"]

    groups = conn.execute(
        """
        SELECT g.*, COUNT(DISTINCT gm.family_id) as member_count
        FROM groups g
        LEFT JOIN group_members gm ON g.id = gm.group_id
        WHERE g.coach_id = ?
        GROUP BY g.id
    """,
        (coach_id,),
    ).fetchall()

    # Get schedules and members for each group, grouped by schedule slot
    group_schedules = {}
    group_members = {}

    DAYS = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    for group in groups:
        # Get all schedule slots for this group
        schedules = conn.execute(
            """
            SELECT id, day_of_week, start_time, end_time
            FROM group_schedules
            WHERE group_id = ?
            ORDER BY day_of_week, start_time
        """,
            (group["id"],),
        ).fetchall()
        group_schedules[group["id"]] = [
            {
                "id": s["id"],
                "day": DAYS[s["day_of_week"]],
                "time": s["start_time"],
                "label": f"{DAYS[s['day_of_week']]} {s['start_time']}",
            }
            for s in schedules
        ]

        # Get members grouped by their schedule
        members_by_schedule = {}
        for schedule in schedules:
            members = conn.execute(
                """
                SELECT gm.kid_name, u.full_name as parent_name, u.email, u.phone
                FROM group_members gm
                JOIN users u ON gm.family_id = u.id
                WHERE gm.group_id = ? AND gm.schedule_id = ?
            """,
                (group["id"], schedule["id"]),
            ).fetchall()
            if members:
                members_by_schedule[schedule["id"]] = members

        # Also get members without a specific schedule
        unscheduled = conn.execute(
            """
            SELECT gm.kid_name, u.full_name as parent_name, u.email, u.phone
            FROM group_members gm
            JOIN users u ON gm.family_id = u.id
            WHERE gm.group_id = ? AND gm.schedule_id IS NULL
        """,
            (group["id"],),
        ).fetchall()
        if unscheduled:
            members_by_schedule[None] = unscheduled

        group_members[group["id"]] = members_by_schedule

    conn.close()
    return render_template(
        "coach/my_groups.html",
        groups=groups,
        group_members=group_members,
        group_schedules=group_schedules,
    )


# ==================== FAMILY ROUTES ====================


@app.route("/family/my-messages")
@login_required
@cache_response(max_age=300)
def family_messages():
    if session["role"] != "family":
        return redirect(url_for("dashboard"))

    conn = get_db()
    user_id = session["user_id"]

    my_groups = conn.execute(
        "SELECT group_id FROM group_members WHERE family_id = ?", (user_id,)
    ).fetchall()
    my_group_ids = [g["group_id"] for g in my_groups]

    messages = []
    if my_group_ids:
        placeholders = ",".join("?" * len(my_group_ids))
        messages = conn.execute(
            f"""
            SELECT m.*, u.full_name as sender_name, g.name as group_name
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            LEFT JOIN groups g ON m.group_id = g.id
            WHERE m.group_id IN ({placeholders}) OR m.is_general = 1
            ORDER BY m.sent_at DESC
        """,
            tuple(my_group_ids),
        ).fetchall()

    conn.close()
    return render_template("family/messages.html", messages=messages)


@app.route("/family/my-enrollments")
@login_required
@cache_response(max_age=300)
def family_enrollments():
    if session["role"] != "family":
        return redirect(url_for("dashboard"))

    conn = get_db()
    user_id = session["user_id"]

    enrollments = conn.execute(
        """
        SELECT g.*, gm.kid_name, u.full_name as coach_name
        FROM group_members gm
        JOIN groups g ON gm.group_id = g.id
        LEFT JOIN users u ON g.coach_id = u.id
        WHERE gm.family_id = ?
    """,
        (user_id,),
    ).fetchall()

    conn.close()
    return render_template("family/enrollments.html", enrollments=enrollments)


# ==================== SETUP ROUTE ====================


@app.route("/setup", methods=["GET", "POST"])
def setup():
    """Create admin user if no users exist."""
    conn = get_db()
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()

    if user_count > 0:
        flash("Setup already completed.", "info")
        return redirect(url_for("login"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()

        if not email or not password or not full_name:
            flash("All fields are required.", "danger")
            return render_template("setup.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("setup.html")

        conn = get_db()
        try:
            hashed_password = generate_password_hash(password)
            conn.execute(
                """
                INSERT INTO users (email, password, full_name, role)
                VALUES (?, ?, ?, 'admin')
            """,
                (email, hashed_password, full_name),
            )
            conn.commit()
            flash("Admin account created! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already exists.", "danger")
        finally:
            conn.close()

    return render_template("setup.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5001)


# Vercel deployment - added handler
def handler(request):
    return app(request)
