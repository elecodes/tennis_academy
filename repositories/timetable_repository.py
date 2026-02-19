import sqlite3
from datetime import datetime, timedelta

class TimetableRepository:
    """
    Repository for accessing timetable data with RBAC.
    Works with group_members table (not group_schedules).
    """
    
    def __init__(self, db_path):
        self.db_path = db_path
    
    def get_weekly_timetable(self, role, user_id, week_start_date):
        """
        Get weekly timetable based on user role.
        
        Args:
            role: 'admin', 'coach', or 'family'
            user_id: User ID from session
            week_start_date: datetime.date object (must be Monday)
        
        Returns:
            dict with 'groups' list and week info
        """
        
        if week_start_date.weekday() != 0:
            raise ValueError("week_start must be a Monday")
        
        week_end = week_start_date + timedelta(days=6)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            if role == 'admin':
                groups = self._get_admin_groups(cursor, week_start_date, week_end)
            elif role == 'coach':
                groups = self._get_coach_groups(cursor, user_id, week_start_date, week_end)
            elif role == 'family':
                groups = self._get_family_groups(cursor, user_id, week_start_date, week_end)
            else:
                raise ValueError(f"Invalid role: {role}")
            
            return {
                'groups': groups,
                'week_start': week_start_date.strftime('%A, %B %d, %Y'),
                'week_end': week_end.strftime('%A, %B %d, %Y'),
            }
        
        finally:
            conn.close()
    
    def _get_admin_groups(self, cursor, week_start, week_end):
        """Admin sees ALL groups"""
        query = '''
            SELECT 
                g.id,
                g.name,
                g.schedule,
                'All Ages' as level,
                u.id as coach_id,
                u.full_name as coach_name,
                u.email as coach_email
            FROM groups g
            LEFT JOIN users u ON g.coach_id = u.id
            ORDER BY g.name
        '''
        cursor.execute(query)
        groups_data = cursor.fetchall()
        
        return self._enrich_groups(cursor, groups_data, week_start, week_end)
    
    def _get_coach_groups(self, cursor, user_id, week_start, week_end):
        """Coach sees ONLY their assigned groups"""
        query = '''
            SELECT 
                g.id,
                g.name,
                g.schedule,
                'All Ages' as level,
                u.id as coach_id,
                u.full_name as coach_name,
                u.email as coach_email
            FROM groups g
            LEFT JOIN users u ON g.coach_id = u.id
            WHERE g.coach_id = ?
            ORDER BY g.name
        '''
        cursor.execute(query, (user_id,))
        groups_data = cursor.fetchall()
        
        return self._enrich_groups(cursor, groups_data, week_start, week_end)
    
    def _get_family_groups(self, cursor, user_id, week_start, week_end):
        """Family sees ONLY their enrolled groups (via group_members)"""
        query = '''
            SELECT DISTINCT
                g.id,
                g.name,
                g.schedule,
                'All Ages' as level,
                u.id as coach_id,
                u.full_name as coach_name,
                u.email as coach_email
            FROM groups g
            LEFT JOIN users u ON g.coach_id = u.id
            WHERE g.id IN (
                SELECT DISTINCT group_id 
                FROM group_members 
                WHERE family_id = ?
            )
            ORDER BY g.name
        '''
        cursor.execute(query, (user_id,))
        groups_data = cursor.fetchall()
        
        return self._enrich_groups(cursor, groups_data, week_start, week_end)
    
    def _enrich_groups(self, cursor, groups_data, week_start, week_end):
        """Add kids and schedules to each group"""
        groups = []
        
        for g in groups_data:
            group_id = g['id']
            
            # Get kids in this group
            kids_query = '''
                SELECT DISTINCT
                    gm.kid_name as name,
                    'Unknown' as age
                FROM group_members gm
                WHERE gm.group_id = ?
            '''
            cursor.execute(kids_query, (group_id,))
            kids = [dict(row) for row in cursor.fetchall()]
            
            # Get structured schedules from the new table
            schedules_query = '''
                SELECT id, day_of_week as day, start_time, end_time, court
                FROM group_schedules
                WHERE group_id = ?
                ORDER BY day_of_week, start_time
            '''
            cursor.execute(schedules_query, (group_id,))
            schedules = [dict(row) for row in cursor.fetchall()]
            
            groups.append({
                'id': g['id'],
                'name': g['name'],
                'schedule_text': g['schedule'],
                'level': g['level'],
                'coach': {
                    'id': g['coach_id'],
                    'name': g['coach_name'] or 'TBD',
                    'email': g['coach_email'],
                },
                'kids': kids,
                'schedules': schedules,
            })
        
        return groups

    def add_session(self, group_id, day, start, end, court='Court 1'):
        """Add a new session to a group"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO group_schedules (group_id, day_of_week, start_time, end_time, court)
                VALUES (?, ?, ?, ?, ?)
            ''', (group_id, day, start, end, court))
            conn.commit()
            return True
        finally:
            conn.close()

    def delete_session(self, session_id):
        """Delete a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM group_schedules WHERE id = ?', (session_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_all_groups(self):
        """Get list of all groups (for Admin dropdowns)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id, name FROM groups ORDER BY name')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def _parse_schedule(self, schedule_text):
        """
        Parse schedule text into structured format.
        Examples:
        - "Monday & Wednesday 4:00-5:30 PM"
        - "Tuesday & Thursday 4:00-5:30 PM"
        - "Saturday 9:00-11:00 AM"
        
        Returns list of dicts with day, start_time, end_time, court
        """
        if not schedule_text:
            return []
        
        # Simple parser - improve as needed
        days_map = {
            'Monday': 0, 'Mon': 0,
            'Tuesday': 1, 'Tue': 1,
            'Wednesday': 2, 'Wed': 2,
            'Thursday': 3, 'Thu': 3,
            'Friday': 4, 'Fri': 4,
            'Saturday': 5, 'Sat': 5,
            'Sunday': 6, 'Sun': 6,
        }
        
        schedules = []
        
        # Split by " & " to handle multiple days
        parts = schedule_text.split(' & ')
        
        # Last part contains time info
        time_part = parts[-1] if parts else ""
        
        # Extract times (e.g., "4:00-5:30 PM")
        times = []
        if '-' in time_part:
            time_range = time_part.split()[0]  # Get "4:00-5:30"
            if '-' in time_range:
                start, end = time_range.split('-')
                times = [start.strip(), end.strip()]
        
        start_time = times[0] if times else "4:00"
        end_time = times[1] if len(times) > 1 else "5:30"
        
        # Extract days
        for part in parts[:-1]:  # All but last part are days
            for day_name, day_num in days_map.items():
                if day_name.lower() in part.lower():
                    schedules.append({
                        'day': day_num,
                        'start_time': start_time,
                        'end_time': end_time,
                        'court': 'Court 1',  # Default court
                    })
                    break
        
        # Handle last part if it has a day
        last_part = parts[-1]
        for day_name, day_num in days_map.items():
            if day_name.lower() in last_part.lower():
                schedules.append({
                    'day': day_num,
                    'start_time': start_time,
                    'end_time': end_time,
                    'court': 'Court 1',  # Default court
                })
                break
        
        return schedules