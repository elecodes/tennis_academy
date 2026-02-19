-- ============================================================================
-- MIGRATION: 002_insert_sample_data.sql
-- PURPOSE: Insert sample data for testing and development
-- CREATED: 2026-02-18
-- ============================================================================

INSERT OR IGNORE INTO coaches (id, name, email, phone) VALUES
('coach-1', 'Miguel García', 'miguel.garcia@tennis-academy.com', '+34 912 345 678'),
('coach-2', 'Carmen Rodríguez', 'carmen.rodriguez@tennis-academy.com', '+34 912 345 679'),
('coach-3', 'Juan López', 'juan.lopez@tennis-academy.com', '+34 912 345 680');

INSERT OR IGNORE INTO families (id, email, name) VALUES
('fam-1', 'garcia.family@gmail.com', 'García Family'),
('fam-2', 'rodriguez.family@gmail.com', 'Rodríguez Family'),
('fam-3', 'lopez.family@gmail.com', 'López Family'),
('fam-4', 'martinez.family@gmail.com', 'Martínez Family');

INSERT OR IGNORE INTO kids (id, family_id, name, age) VALUES
('kid-1', 'fam-1', 'Sofia García', 11),
('kid-2', 'fam-1', 'Juan García', 9),
('kid-3', 'fam-2', 'Ana Rodríguez', 12),
('kid-4', 'fam-3', 'Carlos López', 10),
('kid-5', 'fam-4', 'María Martínez', 13),
('kid-6', 'fam-4', 'David Martínez', 11);

INSERT OR IGNORE INTO groups (id, name, coach_id, level) VALUES
('group-1', 'U-12 Beginner', 'coach-1', 'Beginner'),
('group-2', 'U-16 Intermediate', 'coach-2', 'Intermediate'),
('group-3', 'U-10 Beginner', 'coach-3', 'Beginner'),
('group-4', 'Advanced Competition', 'coach-1', 'Advanced');

INSERT OR IGNORE INTO group_kids (group_id, kid_id) VALUES
('group-1', 'kid-1'),
('group-1', 'kid-2'),
('group-2', 'kid-3'),
('group-3', 'kid-4'),
('group-2', 'kid-5'),
('group-4', 'kid-6');

INSERT OR IGNORE INTO group_schedules (id, group_id, day_of_week, start_time, end_time, court) VALUES
('sched-1-1', 'group-1', 0, '10:00', '11:00', 'Court 1'),
('sched-1-2', 'group-1', 2, '10:00', '11:00', 'Court 1'),
('sched-1-3', 'group-1', 4, '15:00', '16:00', 'Court 2'),
('sched-2-1', 'group-2', 1, '16:00', '17:00', 'Court 2'),
('sched-2-2', 'group-2', 3, '16:00', '17:00', 'Court 2'),
('sched-2-3', 'group-2', 5, '14:00', '15:30', 'Court 1'),
('sched-3-1', 'group-3', 0, '09:00', '10:00', 'Court 3'),
('sched-3-2', 'group-3', 2, '09:00', '10:00', 'Court 3'),
('sched-3-3', 'group-3', 4, '17:00', '18:00', 'Court 3'),
('sched-4-1', 'group-4', 1, '17:30', '19:00', 'Court 1'),
('sched-4-2', 'group-4', 3, '17:30', '19:00', 'Court 1'),
('sched-4-3', 'group-4', 5, '10:00', '12:00', 'Court 1');