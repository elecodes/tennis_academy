-- ============================================================================
-- MIGRATION: 001_create_groups_timetable.sql
-- DB: SQLite
-- PURPOSE: Create tables for group management and weekly timetables
-- CREATED: 2026-02-18
-- ============================================================================

-- ============================================================================
-- 1. COACHES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS coaches (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_coaches_email ON coaches(email);

-- ============================================================================
-- 2. FAMILIES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS families (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_families_email ON families(email);

-- ============================================================================
-- 3. KIDS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS kids (
    id TEXT PRIMARY KEY,
    family_id TEXT NOT NULL,
    name TEXT NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 0 AND age <= 120),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_kids_family_id ON kids(family_id);

-- ============================================================================
-- 4. GROUPS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS groups (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    coach_id TEXT NOT NULL,
    level TEXT NOT NULL CHECK (level IN ('Beginner', 'Intermediate', 'Advanced')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (coach_id) REFERENCES coaches(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_groups_coach_id ON groups(coach_id);
CREATE INDEX IF NOT EXISTS idx_groups_level ON groups(level);

-- ============================================================================
-- 5. GROUP_KIDS JUNCTION TABLE (many-to-many)
-- ============================================================================
CREATE TABLE IF NOT EXISTS group_kids (
    group_id TEXT NOT NULL,
    kid_id TEXT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (group_id, kid_id),
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (kid_id) REFERENCES kids(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_group_kids_group_id ON group_kids(group_id);
CREATE INDEX IF NOT EXISTS idx_group_kids_kid_id ON group_kids(kid_id);

-- ============================================================================
-- 6. GROUP_SCHEDULES TABLE (sesiones semanales)
-- ============================================================================
CREATE TABLE IF NOT EXISTS group_schedules (
    id TEXT PRIMARY KEY,
    group_id TEXT NOT NULL,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    court TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, day_of_week, start_time),
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_group_schedules_group_id ON group_schedules(group_id);
CREATE INDEX IF NOT EXISTS idx_group_schedules_day ON group_schedules(day_of_week);