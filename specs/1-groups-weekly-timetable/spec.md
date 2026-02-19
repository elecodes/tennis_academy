# Feature Spec: Weekly Group Timetables

**Feature ID**: 1-groups-weekly-timetable  
**Status**: Specification  
**Created**: 2026-02-18  
**Author**: Elena  

---

## 📋 Overview

Mostrar **horario semanal de grupos de tenis** con:
- Entrenador (coach)
- Niños en el grupo
- Horarios (día, hora, cancha)
- Control de acceso según rol (RBAC)

---

## 👥 Roles & Acceso

| Rol | Ve | No ve |
|-----|----|----|
| **Admin** | Todos los grupos + emails coaches | — |
| **Coach** | Solo sus grupos asignados | Otros coaches, emails familias |
| **Family** | Solo su grupo + sus niños | Otros niños, otros grupos |

---

## 🎯 Requisitos Funcionales

### RF-1: Vista de Horario Semanal
- **Dado** un usuario autenticado
- **Cuando** accede a "Horarios" o "Weekly Timetable"
- **Entonces** ve tabla con: Grupo | Coach | Lun | Mar | Mié | Jue | Vie | Sab | Dom

### RF-2: Información por Grupo
Cada grupo muestra:
- Nombre del grupo (ej: "U-12 Beginner")
- Nombre del entrenador
- Nivel (Beginner/Intermediate/Advanced)
- Horarios: día, hora inicio/fin, cancha

### RF-3: Información de Niños
- Lista de niños en el grupo
- Edad de cada niño
- Solo visible para: Admin, Coach (su grupo), Family (sus niños)

### RF-4: Control de Acceso (RBAC)
- **Admin**: Ve todos los grupos, todos los niños, emails de coaches
- **Coach**: Ve solo sus grupos, sin emails de familias
- **Family**: Ve solo su grupo, solo sus niños

### RF-5: Responsive Design
- Mobile-first
- Tablas legibles en pantallas pequeñas

---

## 🗄️ Base de Datos (SQLite)

### Tablas Creadas ✅

#### `coaches`
```
id (TEXT, PK)
name (TEXT NOT NULL)
email (TEXT UNIQUE NOT NULL)
phone (TEXT)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

#### `families`
```
id (TEXT, PK)
email (TEXT UNIQUE NOT NULL)
name (TEXT)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

#### `kids`
```
id (TEXT, PK)
family_id (FK → families)
name (TEXT NOT NULL)
age (INTEGER NOT NULL)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

#### `groups`
```
id (TEXT, PK)
name (TEXT UNIQUE NOT NULL)
coach_id (FK → coaches) NOT NULL
level (TEXT: 'Beginner'|'Intermediate'|'Advanced')
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

#### `group_kids` (many-to-many)
```
group_id (FK → groups)
kid_id (FK → kids)
joined_at (TIMESTAMP)
PRIMARY KEY (group_id, kid_id)
```

#### `group_schedules`
```
id (TEXT, PK)
group_id (FK → groups)
day_of_week (INT: 0=Lun, 6=Dom)
start_time (TEXT: "10:00")
end_time (TEXT: "11:00")
court (TEXT: "Court 1")
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

---

## 🔌 API Endpoints

### GET /api/timetables/weekly?date=2026-02-16

**Response (Admin)**:
```json
{
  "week_start": "2026-02-16",
  "week_end": "2026-02-22",
  "groups": [
    {
      "id": "group-1",
      "name": "U-12 Beginner",
      "level": "Beginner",
      "coach": {
        "id": "coach-1",
        "name": "Miguel García",
        "email": "miguel@academy.com"
      },
      "schedules": [
        {"day": "MON", "start": "10:00", "end": "11:00", "court": "Court 1"},
        {"day": "WED", "start": "10:00", "end": "11:00", "court": "Court 1"}
      ],
      "kids": [
        {"id": "kid-1", "name": "Sofia", "age": 11},
        {"id": "kid-2", "name": "Juan", "age": 9}
      ]
    }
  ]
}
```

**Response (Coach - sin email)**:
```json
{
  "groups": [
    {
      "id": "group-1",
      "name": "U-12 Beginner",
      "coach": {
        "id": "coach-1",
        "name": "Miguel García"
      },
      "schedules": [...],
      "kids": [...]
    }
  ]
}
```

**Response (Family - solo sus niños)**:
```json
{
  "groups": [
    {
      "id": "group-1",
      "name": "U-12 Beginner",
      "coach": {"id": "coach-1", "name": "Miguel García"},
      "schedules": [...],
      "kids": [
        {"id": "kid-1", "name": "Sofia", "age": 11},
        {"id": "kid-2", "name": "Juan", "age": 9}
      ]
    }
  ]
}
```

---

## 🎨 Wireframe

```
┌─────────────────────────────────────────────────┐
│  🎾 Tennis Academy - Weekly Schedules            │
├─────────────────────────────────────────────────┤
│                                                   │
│  [← Week]  MON 16 - SUN 22 FEB  [Week →]        │
│                                                   │
│  GROUP: U-12 Beginner (Level: Beginner)         │
│  Coach: Miguel García                            │
│  ┌──────┬──────┬──────┬──────┬──────┬──────┬────┐
│  │ MON  │ TUE  │ WED  │ THU  │ FRI  │ SAT  │SUN │
│  │ 10h  │  -   │ 10h  │  -   │ 15h  │ 14h  │ -  │
│  │ Ct 1 │      │ Ct 1 │      │ Ct 2 │ Ct 1 │    │
│  └──────┴──────┴──────┴──────┴──────┴──────┴────┘
│
│  Kids in group (3):
│  • Sofia García, 11 años
│  • Juan García, 9 años
│  • Ana Pérez, 10 años
│
│  ───────────────────────────────────────────────
│
│  GROUP: U-16 Intermediate (Level: Intermediate)
│  Coach: Carmen Rodríguez
│  [similar structure]
│
└─────────────────────────────────────────────────┘
```

---

## 🧪 User Scenarios

### Scenario 1: Admin Views All Groups
```
Given: Admin logged in
When:  Clicks "Schedules" menu
Then:  Sees all 5 groups with all details
And:   Sees coach emails
And:   Can filter by level/coach
```

### Scenario 2: Coach Views Only Assigned Groups
```
Given: Coach logged in
When:  Clicks "My Groups"
Then:  Sees only 2 groups assigned to him
And:   Sees all kids in his groups
And:   Does NOT see emails of families
And:   Does NOT see other coaches' groups
```

### Scenario 3: Family Views Only Their Group
```
Given: Family logged in with 2 kids in same group
When:  Clicks "My Group Schedule"
Then:  Sees 1 group (their group)
And:   Sees only their 2 kids listed
And:   Does NOT see other families' kids
And:   Sees coach name (not email)
```

### Scenario 4: Week Navigation
```
Given: User viewing week of Feb 16-22
When:  Clicks "← Previous Week" or "Next Week →"
Then:  Schedule updates to previous/next week
And:   URL updates: ?date=2026-02-09 (or 2026-02-23)
```

---

## ✅ Acceptance Criteria

- [ ] Tablas SQLite creadas con migraciones ✅
- [ ] API endpoint GET /api/timetables/weekly funcional
- [ ] RBAC implementado: Admin, Coach, Family ven datos correctos
- [ ] Datos sensibles (emails) ocultos según rol
- [ ] Responsive en mobile (≥320px ancho)
- [ ] Tests unitarios: ≥90% coverage en lógica
- [ ] Tests integración: API + BD
- [ ] Frontend: HTML + Jinja2 renderiza correctamente
- [ ] Sin leaks de PII (emails, family_id innecesarios)

---

## 🛠️ Implementation Stack

| Layer | Technology | Nota |
|-------|-----------|------|
| BD | SQLite ✅ | Migraciones en `/migrations` |
| Backend | Flask + Python | Existing app.py |
| Lógica | Repository Pattern | RBAC en queries |
| Frontend | Jinja2 + HTML/CSS | Templates en `/templates` |
| Tests | pytest | TDD: tests primero |

---

## 📅 Timeline Estimado

| Tarea | Duración |
|-------|----------|
| Repository + RBAC | 45 min |
| API endpoint | 30 min |
| Tests | 60 min |
| Frontend | 60 min |
| QA + fixes | 30 min |
| **Total** | **~3.5 horas** |
