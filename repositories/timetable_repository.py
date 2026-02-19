"""
Repository para acceso a horarios semanales con control RBAC.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class TimetableRepository:
    """Acceso a datos de horarios semanales"""

    def __init__(self, db_path: str = 'academy.db'):
        self.db_path = db_path

    def _get_connection(self):
        """Abre conexión a BD"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_weekly_timetable(
        self,
        user_role: str,
        user_id: str,
        week_start_date: datetime
    ) -> Dict:
        """
        Obtiene horario semanal según rol del usuario.
        
        Args:
            user_role: 'admin', 'coach', o 'family'
            user_id: ID del usuario autenticado
            week_start_date: Lunes de la semana
        
        Returns:
            Dict con week_start, week_end, y lista de grupos
        """
        # Validar que es lunes
        if week_start_date.weekday() != 0:
            raise ValueError("week_start_date debe ser un lunes (weekday=0)")

        week_end_date = week_start_date + timedelta(days=6)

        if user_role == 'admin':
            groups = self._get_all_groups_admin()
        elif user_role == 'coach':
            groups = self._get_coach_groups(user_id)
        elif user_role == 'family':
            groups = self._get_family_groups(user_id)
        else:
            raise ValueError(f"Rol inválido: {user_role}")

        return {
            'week_start': week_start_date.strftime('%Y-%m-%d'),
            'week_end': week_end_date.strftime('%Y-%m-%d'),
            'groups': groups
        }

    def _get_all_groups_admin(self) -> List[Dict]:
        """ADMIN: Todos los grupos con detalles completos"""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = """
        SELECT 
            g.id,
            g.name,
            g.level,
            c.id as coach_id,
            c.name as coach_name,
            c.email as coach_email
        FROM groups g
        JOIN coaches c ON g.coach_id = c.id
        ORDER BY g.name
        """

        cursor.execute(query)
        groups_raw = cursor.fetchall()

        groups = []
        for group_row in groups_raw:
            group_id = group_row['id']
            
            # Obtener horarios
            schedules = self._get_schedules(group_id, conn)
            
            # Obtener niños
            kids = self._get_kids_in_group(group_id, conn)

            group_dict = {
                'id': group_id,
                'name': group_row['name'],
                'level': group_row['level'],
                'coach': {
                    'id': group_row['coach_id'],
                    'name': group_row['coach_name'],
                    'email': group_row['coach_email']  # ✅ ADMIN ve emails
                },
                'schedules': schedules,
                'kids': kids
            }
            groups.append(group_dict)

        conn.close()
        return groups

    def _get_coach_groups(self, coach_id: str) -> List[Dict]:
        """COACH: Solo sus grupos, sin emails de familias"""
        conn = self._get_connection()
        cursor = conn.cursor()

        query = """
        SELECT 
            g.id,
            g.name,
            g.level,
            c.id as coach_id,
            c.name as coach_name
        FROM groups g
        JOIN coaches c ON g.coach_id = c.id
        WHERE g.coach_id = ?
        ORDER BY g.name
        """

        cursor.execute(query, (coach_id,))
        groups_raw = cursor.fetchall()

        groups = []
        for group_row in groups_raw:
            group_id = group_row['id']
            
            schedules = self._get_schedules(group_id, conn)
            kids = self._get_kids_in_group(group_id, conn, include_family_id=False)

            group_dict = {
                'id': group_id,
                'name': group_row['name'],
                'level': group_row['level'],
                'coach': {
                    'id': group_row['coach_id'],
                    'name': group_row['coach_name']
                    # ❌ NO email para coaches (privacidad familias)
                },
                'schedules': schedules,
                'kids': kids
            }
            groups.append(group_dict)

        conn.close()
        return groups

    def _get_family_groups(self, family_id: str) -> List[Dict]:
        """FAMILY: Solo su grupo, solo sus niños"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Primero obtener los grupos donde tiene niños
        query = """
        SELECT DISTINCT
            g.id,
            g.name,
            g.level,
            c.id as coach_id,
            c.name as coach_name
        FROM groups g
        JOIN coaches c ON g.coach_id = c.id
        JOIN group_kids gk ON g.id = gk.group_id
        JOIN kids k ON gk.kid_id = k.id
        WHERE k.family_id = ?
        ORDER BY g.name
        """

        cursor.execute(query, (family_id,))
        groups_raw = cursor.fetchall()

        groups = []
        for group_row in groups_raw:
            group_id = group_row['id']
            
            schedules = self._get_schedules(group_id, conn)
            kids = self._get_kids_in_group_for_family(group_id, family_id, conn)

            group_dict = {
                'id': group_id,
                'name': group_row['name'],
                'level': group_row['level'],
                'coach': {
                    'id': group_row['coach_id'],
                    'name': group_row['coach_name']
                },
                'schedules': schedules,
                'kids': kids
            }
            groups.append(group_dict)

        conn.close()
        return groups

    def _get_schedules(self, group_id: str, conn) -> List[Dict]:
        """Obtiene horarios de un grupo"""
        cursor = conn.cursor()
        
        days = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'}

        query = """
        SELECT 
            day_of_week,
            start_time,
            end_time,
            court
        FROM group_schedules
        WHERE group_id = ?
        ORDER BY day_of_week, start_time
        """

        cursor.execute(query, (group_id,))
        schedules_raw = cursor.fetchall()

        schedules = []
        for sched in schedules_raw:
            schedules.append({
                'day': days[sched['day_of_week']],
                'start_time': sched['start_time'],
                'end_time': sched['end_time'],
                'court': sched['court']
            })

        return schedules

    def _get_kids_in_group(
        self, 
        group_id: str, 
        conn,
        include_family_id: bool = True
    ) -> List[Dict]:
        """Obtiene niños de un grupo"""
        cursor = conn.cursor()

        query = """
        SELECT 
            k.id,
            k.name,
            k.age,
            k.family_id
        FROM kids k
        JOIN group_kids gk ON k.id = gk.kid_id
        WHERE gk.group_id = ?
        ORDER BY k.name
        """

        cursor.execute(query, (group_id,))
        kids_raw = cursor.fetchall()

        kids = []
        for kid in kids_raw:
            kid_dict = {
                'id': kid['id'],
                'name': kid['name'],
                'age': kid['age']
            }
            if include_family_id:
                kid_dict['family_id'] = kid['family_id']
            
            kids.append(kid_dict)

        return kids

    def _get_kids_in_group_for_family(
        self, 
        group_id: str, 
        family_id: str,
        conn
    ) -> List[Dict]:
        """Obtiene SOLO los niños de una familia en un grupo"""
        cursor = conn.cursor()

        query = """
        SELECT 
            k.id,
            k.name,
            k.age
        FROM kids k
        JOIN group_kids gk ON k.id = gk.kid_id
        WHERE gk.group_id = ? AND k.family_id = ?
        ORDER BY k.name
        """

        cursor.execute(query, (group_id, family_id))
        kids_raw = cursor.fetchall()

        kids = []
        for kid in kids_raw:
            kids.append({
                'id': kid['id'],
                'name': kid['name'],
                'age': kid['age']
            })

        return kids