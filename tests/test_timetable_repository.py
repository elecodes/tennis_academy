"""
Tests unitarios para TimetableRepository.
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime
from repositories.timetable_repository import TimetableRepository

@pytest.fixture
def test_db_file():
    """Crea BD temporal para tests"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Crear tablas
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    cursor.executescript("""
        CREATE TABLE coaches (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE families (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE kids (
            id TEXT PRIMARY KEY,
            family_id TEXT NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (family_id) REFERENCES families(id)
        );
        
        CREATE TABLE groups (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            coach_id TEXT NOT NULL,
            level TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (coach_id) REFERENCES coaches(id)
        );
        
        CREATE TABLE group_kids (
            group_id TEXT NOT NULL,
            kid_id TEXT NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (group_id, kid_id),
            FOREIGN KEY (group_id) REFERENCES groups(id),
            FOREIGN KEY (kid_id) REFERENCES kids(id)
        );
        
        CREATE TABLE group_schedules (
            id TEXT PRIMARY KEY,
            group_id TEXT NOT NULL,
            day_of_week INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            court TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups(id)
        );
    """)
    
    # Insertar datos de prueba
    cursor.execute("INSERT INTO coaches VALUES ('coach-1', 'Miguel García', 'miguel@academy.com', '123456', datetime('now'), datetime('now'))")
    cursor.execute("INSERT INTO coaches VALUES ('coach-2', 'Carmen Rodríguez', 'carmen@academy.com', '123457', datetime('now'), datetime('now'))")
    
    cursor.execute("INSERT INTO families VALUES ('fam-1', 'garcia@example.com', 'García Family', datetime('now'), datetime('now'))")
    cursor.execute("INSERT INTO families VALUES ('fam-2', 'rodriguez@example.com', 'Rodríguez Family', datetime('now'), datetime('now'))")
    
    cursor.execute("INSERT INTO kids VALUES ('kid-1', 'fam-1', 'Sofia', 11, datetime('now'), datetime('now'))")
    cursor.execute("INSERT INTO kids VALUES ('kid-2', 'fam-1', 'Juan', 9, datetime('now'), datetime('now'))")
    cursor.execute("INSERT INTO kids VALUES ('kid-3', 'fam-2', 'Ana', 12, datetime('now'), datetime('now'))")
    
    cursor.execute("INSERT INTO groups VALUES ('group-1', 'U-12 Beginner', 'coach-1', 'Beginner', datetime('now'), datetime('now'))")
    cursor.execute("INSERT INTO groups VALUES ('group-2', 'U-16 Intermediate', 'coach-2', 'Intermediate', datetime('now'), datetime('now'))")
    
    cursor.execute("INSERT INTO group_kids VALUES ('group-1', 'kid-1', datetime('now'))")
    cursor.execute("INSERT INTO group_kids VALUES ('group-1', 'kid-2', datetime('now'))")
    cursor.execute("INSERT INTO group_kids VALUES ('group-2', 'kid-3', datetime('now'))")
    
    cursor.execute("INSERT INTO group_schedules VALUES ('sched-1', 'group-1', 0, '10:00', '11:00', 'Court 1', datetime('now'), datetime('now'))")
    cursor.execute("INSERT INTO group_schedules VALUES ('sched-2', 'group-1', 2, '10:00', '11:00', 'Court 1', datetime('now'), datetime('now'))")
    
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
        
        result = repo.get_weekly_timetable('admin', 'admin-1', monday)
        
        assert 'groups' in result
        assert len(result['groups']) == 2
    
    def test_admin_sees_coach_emails(self, test_db_file):
        """ADMIN ve emails de coaches"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()
        
        result = repo.get_weekly_timetable('admin', 'admin-1', monday)
        
        # Verificar que hay email en coaches
        for group in result['groups']:
            assert 'email' in group['coach']
            assert group['coach']['email'] is not None
            assert '@' in group['coach']['email']


# ============ TESTS: COACH ============

class TestCoachViewsTimetable:
    """COACH ve solo sus grupos"""
    
    def test_coach_sees_only_assigned_groups(self, test_db_file):
        """COACH ve solo sus grupos"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()
        
        result = repo.get_weekly_timetable('coach', 'coach-1', monday)
        
        assert len(result['groups']) == 1
        assert result['groups'][0]['name'] == 'U-12 Beginner'
    
    def test_coach_no_family_emails(self, test_db_file):
        """COACH NO ve emails de familias"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()
        
        result = repo.get_weekly_timetable('coach', 'coach-1', monday)
        
        for group in result['groups']:
            # Email NO debe estar para coaches
            assert 'email' not in group['coach']
    
    def test_coach_sees_kid_names(self, test_db_file):
        """COACH ve nombres de niños"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()
        
        result = repo.get_weekly_timetable('coach', 'coach-1', monday)
        
        group = result['groups'][0]
        assert len(group['kids']) == 2
        kid_names = [k['name'] for k in group['kids']]
        assert 'Sofia' in kid_names
        assert 'Juan' in kid_names


# ============ TESTS: FAMILY ============

class TestFamilyViewsTimetable:
    """FAMILY ve solo su grupo"""
    
    def test_family_sees_only_their_group(self, test_db_file):
        """FAMILY ve solo su grupo"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()
        
        result = repo.get_weekly_timetable('family', 'fam-1', monday)
        
        assert len(result['groups']) == 1
        assert result['groups'][0]['name'] == 'U-12 Beginner'
    
    def test_family_sees_only_their_kids(self, test_db_file):
        """FAMILY ve solo sus niños"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()
        
        result = repo.get_weekly_timetable('family', 'fam-1', monday)
        
        group = result['groups'][0]
        kids_names = [k['name'] for k in group['kids']]
        
        assert 'Sofia' in kids_names
        assert 'Juan' in kids_names
        assert len(group['kids']) == 2
        
        # Verificar que NO ve otros niños
        assert 'Ana' not in kids_names
    
    def test_family_cannot_see_other_families_groups(self, test_db_file):
        """FAMILY NO ve grupos de otras familias"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()
        
        result = repo.get_weekly_timetable('family', 'fam-1', monday)
        
        # Familia 1 solo debe ver su grupo
        group_names = [g['name'] for g in result['groups']]
        assert 'U-12 Beginner' in group_names
        assert 'U-16 Intermediate' not in group_names


# ============ TESTS: EDGE CASES ============

class TestEdgeCases:
    """Casos límite"""
    
    def test_error_if_not_monday(self, test_db_file):
        """Error si fecha no es lunes"""
        repo = TimetableRepository(test_db_file)
        tuesday = datetime(2026, 2, 17).date()
        
        with pytest.raises(ValueError, match="debe ser un lunes"):
            repo.get_weekly_timetable('admin', 'admin-1', tuesday)
    
    def test_invalid_role(self, test_db_file):
        """Error si rol es inválido"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()
        
        with pytest.raises(ValueError, match="Rol inválido"):
            repo.get_weekly_timetable('invalid_role', 'user-1', monday)
    
    def test_empty_timetable_if_no_groups(self, test_db_file):
        """Si familia sin grupos, devuelve lista vacía"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()
        
        result = repo.get_weekly_timetable('family', 'fam-999', monday)
        
        assert result['groups'] == []
    
    def test_week_dates_correct(self, test_db_file):
        """Las fechas de semana son correctas"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()
        
        result = repo.get_weekly_timetable('admin', 'admin-1', monday)
        
        assert result['week_start'] == '2026-02-16'
        assert result['week_end'] == '2026-02-22'
    
    def test_schedules_present(self, test_db_file):
        """Los horarios están presentes"""
        repo = TimetableRepository(test_db_file)
        monday = datetime(2026, 2, 16).date()
        
        result = repo.get_weekly_timetable('admin', 'admin-1', monday)
        
        group = result['groups'][0]
        assert 'schedules' in group
        assert len(group['schedules']) > 0
        
        schedule = group['schedules'][0]
        assert 'day' in schedule
        assert 'start_time' in schedule
        assert 'end_time' in schedule
        assert 'court' in schedule