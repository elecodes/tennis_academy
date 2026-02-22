"""
API routes para horarios semanales.
"""

from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    session,
    redirect,
    url_for,
)
from datetime import datetime, timedelta
from repositories.timetable_repository import TimetableRepository
import os

timetables_bp = Blueprint("timetables", __name__)


@timetables_bp.route("/timetable")
def get_timetable_page():
    """
    GET /timetable?date=2026-02-16
    Página web de horarios semanales.
    """
    # Verificar autenticación
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Obtener fecha de parámetro o usar hoy
    date_str = request.args.get("date")

    if date_str:
        try:
            current_date = datetime.fromisoformat(date_str).date()
        except ValueError:
            current_date = datetime.now().date()
    else:
        current_date = datetime.now().date()

    # Obtener el lunes de esa semana
    week_start = current_date - timedelta(days=current_date.weekday())

    # Calcular semanas anterior y siguiente
    prev_week = (week_start - timedelta(days=7)).strftime("%Y-%m-%d")
    next_week = (week_start + timedelta(days=7)).strftime("%Y-%m-%d")

    try:
        user_id = session.get("user_id")
        user_role = session.get("role", "family")

        # Obtener la ruta a academy.db (now 2 levels up from backend/routes/)
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "academy.db")
        repository = TimetableRepository(db_path)
        result = repository.get_weekly_timetable(user_role, user_id, week_start)

        # Get all groups for the "Add Session" modal if Admin
        all_groups = []
        if user_role == "admin":
            all_groups = repository.get_all_groups()

        return render_template(
            "timetable.html",
            groups=result["groups"],
            all_groups=all_groups,
            week_start=result["week_start"],
            week_end=result["week_end"],
            prev_week=prev_week,
            next_week=next_week,
        )

    except ValueError as e:
        return render_template("error.html", error=str(e)), 400
    except Exception as e:
        print(f"Error: {str(e)}")
        return (
            render_template("error.html", error=f"Error loading schedules: {str(e)}"),
            500,
        )


@timetables_bp.route("/api/timetables/weekly", methods=["GET"])
def get_weekly_timetable_api():
    """
    GET /api/timetables/weekly?date=2026-02-16
    API JSON para horarios semanales con control RBAC.
    """

    # Verificar autenticación
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    # Obtener parámetros
    date_str = request.args.get("date")
    if not date_str:
        return jsonify({"error": "Missing date parameter"}), 400

    # Validar formato de fecha
    try:
        week_start_date = datetime.fromisoformat(date_str).date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Validar que sea lunes
    if week_start_date.weekday() != 0:
        return jsonify({"error": "Date must be a Monday (weekday=0)"}), 400

    try:
        user_id = session["user_id"]
        user_role = session.get("role", "family")

        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "academy.db")
        repository = TimetableRepository(db_path)
        result = repository.get_weekly_timetable(user_role, user_id, week_start_date)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@timetables_bp.route("/admin/timetable/session", methods=["POST"])
def add_timetable_session():
    """POST /admin/timetable/session - Admin adds a session"""
    if "user_id" not in session or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.form
    group_id = data.get("group_id")
    day = data.get("day")
    start = data.get("start_time")
    end = data.get("end_time")
    court = data.get("court", "Court 1")

    if not all([group_id, day, start, end]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "academy.db")
        repository = TimetableRepository(db_path)
        repository.add_session(int(group_id), int(day), start, end, court)
        return redirect(url_for("timetables.get_timetable_page"))
    except Exception as e:
        print(f"Error adding session: {str(e)}")
        return (
            render_template("error.html", error=f"Error adding session: {str(e)}"),
            500,
        )


@timetables_bp.route(
    "/admin/timetable/session/delete/<int:session_id>", methods=["POST"]
)
def delete_timetable_session(session_id):
    """POST /admin/timetable/session/delete/<id> - Admin deletes a session"""
    if "user_id" not in session or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    try:
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "academy.db")
        repository = TimetableRepository(db_path)
        repository.delete_session(session_id)
        return redirect(url_for("timetables.get_timetable_page"))
    except Exception as e:
        print(f"Error deleting session: {str(e)}")
        return (
            render_template("error.html", error=f"Error deleting session: {str(e)}"),
            500,
        )
