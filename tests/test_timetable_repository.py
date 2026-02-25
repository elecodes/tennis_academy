"""
Tests unitarios para TimetableRepository.
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime
from backend.repositories.timetable_repository import TimetableRepository


@pytest.fixture
def test_db_file():
    """Crea BD temporal para tests"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Crear tablas
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'coach', 'family')),
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            schedule TEXT NOT NULL,
            coach_id INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (coach_id) REFERENCES users (id) ON DELETE SET NULL
        );

        CREATE TABLE group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            family_id INTEGER NOT NULL,
            kid_name TEXT NOT NULL,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
            FOREIGN KEY (family_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(group_id, family_id, kid_name)
        );

        CREATE TABLE group_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            court TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
        );
    """)

    # Insert users
    cursor.execute(
        "INSERT INTO users (id, email, password, full_name, role) "
        "VALUES (1, 'admin@academy.com', 'hash', 'Admin User', 'admin')"
    )
    cursor.execute(
        "INSERT INTO users (id, email, password, full_name, role) "
        "VALUES (2, 'coach1@academy.com', 'hash', 'Miguel García', 'coach')"
    )
    cursor.execute(
        "INSERT INTO users (id, email, password, full_name, role) "
        "VALUES (3, 'coach2@academy.com', 'hash', 'Carmen Rodríguez', 'coach')"
    )
    cursor.execute(
        "INSERT INTO users (id, email, password, full_name, role) "
        "VALUES (4, 'fam1@example.com', 'hash', 'García Family', 'family')"
    )
    cursor.execute(
        "INSERT INTO users (id, email, password, full_name, role) "
        "VALUES (5, 'fam2@example.com', 'hash', 'Rodríguez Family', 'family')"
    )

    # Insert groups
    cursor.execute(
        "INSERT INTO groups (id, name, schedule, coach_id, description) "
        "VALUES (1, 'U-12 Beginner', 'Mon/Wed 10:00', 2, 'Beginner')"
    )
    cursor.execute(
        "INSERT INTO groups (id, name, schedule, coach_id, description) "
        "VALUES (2, 'U-16 Intermediate', 'Tue/Thu 10:00', 3, 'Intermediate')"
    )

    # Insert members
    cursor.execute(
        "INSERT INTO group_members (group_id, family_id, kid_name) VALUES (1, 4, 'Sofia')"
    )
    cursor.execute(
        "INSERT INTO group_members (group_id, family_id, kid_name) VALUES (1, 4, 'Juan')"
    )
    # Kid from family 5 also in group 1 to test internal visibility
    cursor.execute(
        "INSERT INTO group_members (group_id, family_id, kid_name) VALUES (1, 5, 'Ana')"
    )
    cursor.execute(
        "INSERT INTO group_members (group_id, family_id, kid_name) VALUES (2, 5, 'Ana')"
    )

    # Insert schedules
    cursor.execute(
        "INSERT INTO group_schedules (group_id, day_of_week, start_time, end_time, court) "
        "VALUES (1, 0, '10:00', '11:00', 'Court 1')"
    )
    cursor.execute(
        "INSERT INTO group_schedules (group_id, day_of_week, start_time, end_time, court) "
        "VALUES (1, 2, '10:00', '11:00', 'Court 1')"
    )
    cursor.execute(
        "INSERT INTO group_schedules (group_id, day_of_week, start_time, end_time, court) "
        "VALUES (2, 1, '10:00', '11:00', 'Court 1')"
    )
    cursor.execute(
        "INSERT INTO group_schedules (group_id, day_of_week, start_time, end_time, court) "
        "VALUES (2, 3, '10:00', '11:00', 'Court 1')"
    )

    conn.commit()
    conn.close()

    yield path

    # Cleanup
    os.unlink(path)


# ============ TESTS: ADMIN ============


class TestAdminViewsTimetable:
    """ADMIN ve todos los grupos"""

    def test_admin_sees_all_groups(self, test_db_file):
        """ADMIN ve todos los grupos"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()

        result = repo.get_weekly_timetable("admin", 1, monday)

        assert "groups" in result
        assert len(result["groups"]) == 2

    def test_admin_sees_coach_emails(self, test_db_file):
        """ADMIN ve emails de coaches"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()

        result = repo.get_weekly_timetable("admin", 1, monday)

        # Verificar que hay email en coaches
        for group in result["groups"]:
            assert "email" in group["coach"]
            assert group["coach"]["email"] is not None
            assert "@" in group["coach"]["email"]


# ============ TESTS: COACH ============


class TestCoachViewsTimetable:
    """COACH ve solo sus grupos"""

    def test_coach_sees_only_assigned_groups(self, test_db_file):
        """COACH ve solo sus grupos"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()

        result = repo.get_weekly_timetable("coach", 2, monday)

        assert len(result["groups"]) == 1
        assert result["groups"][0]["name"] == "U-12 Beginner"

    def test_coach_cannot_see_other_coaches_emails(self, test_db_file):
        """COACH no debe ver emails de otros coaches (en este caso, ni el suyo propio en el listado de grupos)"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()

        result = repo.get_weekly_timetable("coach", 2, monday)

        for group in result["groups"]:
            # Solo Admin debe ver emails
            assert group["coach"]["email"] is None

    def test_coach_sees_kid_names(self, test_db_file):
        """COACH ve nombres de niños"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()

        result = repo.get_weekly_timetable("coach", 2, monday)

        group = result["groups"][0]
        # Sofia, Juan, and now Ana (from a different family) are all in this group
        assert len(group["kids"]) == 3
        kid_names = [k["name"] for k in group["kids"]]
        assert "Sofia" in kid_names
        assert "Juan" in kid_names
        assert "Ana" in kid_names


# ============ TESTS: FAMILY ============


class TestFamilyViewsTimetable:
    """FAMILY ve solo su grupo"""

    def test_family_cannot_see_coach_emails(self, test_db_file):
        """FAMILY no debe ver emails de coaches"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()

        result = repo.get_weekly_timetable("family", 4, monday)

        for group in result["groups"]:
            assert group["coach"]["email"] is None

    def test_family_sees_only_their_group(self, test_db_file):
        """FAMILY ve solo su grupo"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()

        result = repo.get_weekly_timetable("family", 4, monday)

        assert len(result["groups"]) == 1
        assert result["groups"][0]["name"] == "U-12 Beginner"

    def test_family_sees_only_their_kids(self, test_db_file):
        """FAMILY ve solo sus niños, incluso si hay otros en el mismo grupo"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()

        result = repo.get_weekly_timetable("family", 4, monday)

        group = result["groups"][0]
        kids_names = [k["name"] for k in group["kids"]]

        assert "Sofia" in kids_names
        assert "Juan" in kids_names
        assert len(group["kids"]) == 2

        # Verificar que NO ve a 'Ana', que está en el mismo grupo pero es de otra familia (id 5)
        assert "Ana" not in kids_names

    def test_family_cannot_see_other_families_groups(self, test_db_file):
        """FAMILY NO ve grupos de otras familias"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()

        result = repo.get_weekly_timetable("family", 4, monday)

        # Familia 1 solo debe ver su grupo
        group_names = [g["name"] for g in result["groups"]]
        assert "U-12 Beginner" in group_names
        assert "U-16 Intermediate" not in group_names


# ============ TESTS: EDGE CASES ============


class TestEdgeCases:
    """Casos límite"""

    def test_error_if_not_monday(self, test_db_file):
        """Error si fecha no es lunes"""
        repo = TimetableRepository(test_db_file)
        tuesday = datetime(2026, 2, 17).date()

        with pytest.raises(ValueError, match="must be a Monday"):
            repo.get_weekly_timetable("admin", 1, tuesday)

    def test_invalid_role(self, test_db_file):
        """Error si rol es inválido"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()

        with pytest.raises(ValueError, match="Invalid role"):
            repo.get_weekly_timetable("invalid_role", 1, monday)

    def test_empty_timetable_if_no_groups(self, test_db_file):
        """Si familia sin grupos, devuelve lista vacía"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()

        result = repo.get_weekly_timetable("family", 999, monday)

        assert result["groups"] == []

    def test_week_dates_correct(self, test_db_file):
        """Las fechas de semana son correctas"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()

        result = repo.get_weekly_timetable("admin", 1, monday)

        assert "Monday, February 16, 2026" in result["week_start"]
        assert "Sunday, February 22, 2026" in result["week_end"]

    def test_schedules_present(self, test_db_file):
        """Los horarios están presentes"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()

        result = repo.get_weekly_timetable("admin", "admin-1", monday)

        group = result["groups"][0]
        assert "schedules" in group
        assert len(group["schedules"]) > 0

        schedule = group["schedules"][0]
        assert "day" in schedule
        assert "start_time" in schedule
        assert "end_time" in schedule
        assert "court" in schedule

    def test_add_update_delete_session(self, test_db_file):
        """Test CRUD para sesiones individuales"""
        repo = TimetableRepository(test_db_file)

        # Add
        success = repo.add_session(1, 4, "15:00", "16:00", "Court 3")
        assert success is True

        # Verify added
        monday = datetime(2026, 2, 16).date()
        result = repo.get_weekly_timetable("admin", 1, monday)
        group1 = next(g for g in result["groups"] if g["id"] == 1)
        sessions = [s for s in group1["schedules"] if s["court"] == "Court 3"]
        assert len(sessions) == 1
        session_id = sessions[0]["id"]

        # Update
        update_success = repo.update_session(session_id, 4, "15:30", "16:30", "Court 4")
        assert update_success is True

        # Verify updated
        result = repo.get_weekly_timetable("admin", 1, monday)
        group1 = next(g for g in result["groups"] if g["id"] == 1)
        sessions = [s for s in group1["schedules"] if s["court"] == "Court 4"]
        assert len(sessions) == 1
        assert sessions[0]["start_time"] == "15:30"

        # Delete
        delete_success = repo.delete_session(session_id)
        assert delete_success is True

        # Verify deleted
        result = repo.get_weekly_timetable("admin", 1, monday)
        group1 = next(g for g in result["groups"] if g["id"] == 1)
        sessions = [s for s in group1["schedules"] if s["court"] == "Court 4"]
        assert len(sessions) == 0

    def test_get_all_groups(self, test_db_file):
        """Test listado de todos los grupos"""
        repo = TimetableRepository(test_db_file)
        groups = repo.get_all_groups()
        assert len(groups) == 2
        names = [g["name"] for g in groups]
        assert "U-12 Beginner" in names
        assert "U-16 Intermediate" in names

    def test_parse_schedule_logic(self, test_db_file):
        """Test lógica interna de parseo de texto (aunque ya no se use en el flujo principal, está en el repo)"""
        repo = TimetableRepository(test_db_file)

        # Empty
        assert repo._parse_schedule("") == []

        # Simple
        s = repo._parse_schedule("Monday 4:00-5:30 PM")
        assert len(s) == 1
        assert s[0]["day"] == 0
        assert s[0]["start_time"] == "4:00"

        # Multiple days with proper format for this simple parser
        s = repo._parse_schedule("Monday & Wednesday & 4:00-5:30 PM")
        assert len(s) == 2
        assert s[0]["day"] == 0
        assert s[1]["day"] == 2

        # Edge cases for parser
        assert repo._parse_schedule("No days here") == []
