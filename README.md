# SF TENNIS KIDS Club

**Live**: https://tennis-academy-six.vercel.app (Vercel — PG direct → REST API → Turso)
**Backup**: https://sf-tennis-kids.onrender.com (Render — Supabase PostgreSQL direct, PWA-ready)

A simple, free-tier communication platform for tennis clubs to connect administrators, coaches, and families via email notifications.

## 🎯 Features

### Role-Based Access Control (RBAC)
- **Admin**: Full access to manage users, groups, schedules, send messages, audit all communication, and broadcast to Supabase lesson families
- **Coach**: View assigned groups with schedules, send messages to their groups, see family alerts and reply, view message acknowledgments (no family email exposure)
- **Family**: View messages for enrolled groups, acknowledge messages (OK/Received), send preset quick messages to coaches, see weekly schedules

### Weekly Timetables
- **View schedules by week** - Navigate between weeks with a clean 7x1 grid
- **Role-based filtering** - Admins see all, coaches see their groups, families see their kids' groups
- **Supabase timetable** - Family timetable now filters by `parent_email` showing only enrolled lessons
- **Premium Centered Layout** - Elegant, focused experience using `max-w-7xl mx-auto` containers
- **Custom Modal System** - Reliable, vanilla JS interactions for all record creation (no Bootstrap JS dependencies)
- **Responsive design** - Optimized for mobile, tablet, and high-res desktops
- **PWA-ready** - Can be installed on mobile via "Add to Home Screen" for app-like experience
- **Mobile bottom navigation** - Quick access to Home, Schedule, Groups, and Message on mobile
- **Mobile-friendly schedule display** - Compact day/time pills (e.g., "Mon 4pm", "Wed 5:30pm")
- **Day filter buttons** - Filter schedule by day to show only groups with lessons on that day
- **Theme toggle** - Click the palette icon in the header to switch between V1 (original) and V2 (royal blue + golden yellow) themes

### Message Types
- Rain cancellations (urgent)
- Coach delays (urgent)
- General announcements
- Schedule changes

### Key Features
- ✅ Email notifications sent automatically
- ✅ Group-based messaging (coaches message only their groups)
- ✅ General announcements (admin can message all families)
- ✅ Weekly timetable view with RBAC
- ✅ **Turso Cloud Database** (Edge SQLite for real-time sync)
- ✅ **Supabase Integration** (PostgreSQL read layer for students, enrollments, users, coach dashboard, admin dashboard, timetable, family enrollments, and messaging)
- ✅ **Message Acknowledgments** — family clicks "OK" or "Received" on each message; coach sees ack summary in "Messages Sent" table
- ✅ **Family Quick Messages** — 4 presets (Running Late, Will Miss, On My Way, Early Pickup), no free text, 15-min rate limit
- ✅ **Coach Reply** — reply button on family alerts opens modal with free text; creates messages entry + message_recipients for the family
- ✅ **Admin Message Auditor** — `/admin/messages` table of ALL messages (broadcasts + family notes), edit modal, soft delete
- ✅ **Unread message tracking** (`is_read` column + unread count on dashboard + visual read/unread styling)
- ✅ **Mark All Read** — one-click bulk marking on family messages page
- ✅ **Google Spreadsheet Integration** (Sync schedules automatically)
- ✅ **Auto-Sync** (Sheets edits sync to Turso in seconds via installable GAS triggers)
- ✅ Simple web interface for all roles
- ✅ 100% free (Python, Flask, Gmail SMTP)

## 🛠 Tech Stack

| Technology | Component | Cost |
|-----------|-----------|------|
| Backend | Python 3.12 + Flask | Free |
| Database (primary) | Turso Cloud (libSQL) | Free |
| Database (secondary) | Supabase (PostgreSQL) via pg8000 direct + REST API fallback | Free |
| DB Driver (PG) | pg8000 (pure Python, SSL + IPv6) | Free |
| Email | Python smtplib + Gmail | Free |
| Frontend | HTML5 + CSS3 + Bootstrap 5 | Free |
| Validation| **Zod** + esbuild | Free |
| Monitoring | **Sentry** | Free tier |
| Security | **flask-talisman** (Security Headers) | Free |
| CI/CD | GitHub Actions | Free |
| Container | **Docker** + Docker Compose | Free |
| Deployment | Docker / PythonAnywhere / Render / Railway | Free tier available |

## 📦 Installation

### Option A: Docker (Recommended)

#### Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop/) and Docker Compose

#### Quick Start

```bash
# 1. Clone the project
git clone <your-repo-url>
cd tennis_academy

# 2. Set environment variables
export TURSO_URL=libsql://your-db.turso.io
export TURSO_TOKEN=your-token
export SENDER_EMAIL=your-email@gmail.com
export SENDER_PASSWORD=your-app-password

# 3. Build and run
docker compose up --build
```

The app will be available at: **http://localhost:5001**

### Option B: Manual Installation

### 1. Prerequisites
- Python 3.8 or higher
- pip (comes with Python)
- Gmail account (for email notifications)

### 2. Clone/Download Project

```bash
cd tennis_academy
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv

# Activate it:
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 5. Configure Email (Gmail)

To send emails through Gmail:

1. Go to https://myaccount.google.com/
2. Enable **2-Factor Authentication**
3. Go to **Security** → **App Passwords**
4. Select "Mail" and "Windows Computer" (or other device)
5. Copy the **16-character password**

**Set environment variables**:

On Mac/Linux:
```bash
export SENDER_EMAIL=your-email@gmail.com
export SENDER_PASSWORD=xxxx-xxxx-xxxx-xxxx
export TURSO_URL=libsql://your-db.turso.io
export TURSO_TOKEN=your-token
```

On Windows:
```cmd
set SENDER_EMAIL=your-email@gmail.com
set SENDER_PASSWORD=xxxx-xxxx-xxxx-xxxx
set TURSO_URL=libsql://your-db.turso.io
set TURSO_TOKEN=your-token
```

### 6. Run the Application

```bash
python3 backend/app.py
```

The app will be available at: **http://localhost:5001**

### 7. Initial Setup

1. Visit http://localhost:5001/setup
2. Create the admin account
3. Log in with admin credentials
4. Start adding coaches, families, groups, and schedules

## 🚀 Quick Start Guide

### Admin Workflow
```
1. Add Coaches: Admin Panel → Users → Add User (role: Coach)
2. Add Families: Admin Panel → Users → Add User (role: Family)
3. Create Groups: Admin Panel → Groups → Add Group
4. Assign Coach: Select coach when creating group
5. Enroll Kids: Admin Panel → Enrollments → Add Enrollment
6. Send Messages: Admin Panel → Broadcast → Select group or specific schedule slot → Send
7. View Schedules: Dashboard → View Weekly Schedules
8. Audit Messages: Admin Panel → Message Auditor (view/edit/delete all messages)
9. Supabase Broadcast: Nav → Broadcast (Supabase) → select lesson → send
```

### Coach Workflow
```
1. Login with coach credentials
2. Dashboard → My Groups (view assigned groups)
3. Dashboard → Send Message (notify families)
4. Dashboard → Messages from Families (view and reply to quick messages)
5. Dashboard → View Weekly Schedules (see all sessions)
6. Check Acknowledgments column in Messages Sent for family response status
```

### Family Workflow
```
1. Login with family credentials
2. Dashboard → My Enrollments (see kids' groups)
3. Dashboard → Notify Your Coach (send preset quick messages)
4. Dashboard → View Weekly Schedules (see kids' schedules)
5. Dashboard → My Messages (receive notifications, acknowledge with OK/Received, Mark All Read)
6. Email notifications arrive automatically
```

## 📊 Database Schema

```sql
-- Users (admin, coach, family)
users(id, email, password, full_name, role, phone, created_at, is_active)

-- Groups (tennis groups)
groups(id, name, schedule, coach_id, description, created_at, UNIQUE(name, coach_id))

-- Group memberships (enrollments)
group_members(id, group_id, family_id, kid_name, enrolled_at)

-- Weekly schedules (structured data)
group_schedules(id, group_id, day_of_week, start_time, end_time, court, created_at)

-- Messages
messages(id, sender_id, group_id, message_type, subject, content, sent_at, is_general)

-- Message recipients tracking
message_recipients(id, message_id, user_id, email_sent, sent_at, is_read, ack_type, ack_at)

-- Family quick messages (preset-only, no free text for families)
family_quick_messages(id, user_id, group_id, kid_name, coach_name, preset, subject, content, sent_at, is_read, deleted_at)
```

## 📚 Documentation

- **[ADR-001](docs/ADR-001:%20Weekly%20Timetable%20Repository%20Pattern.md)** - Timetable Repository Pattern
- **[ADR-002](docs/ADR-002:%20Vanilla%20JS%20Modal%20System.md)** - Custom Modal System
- **[ADR-003](docs/ADR-003:%20Agentic%20Guardians%20and%20Testing%20Strategy.md)** - Agentic Guardians
- **[ADR-007](docs/ADR-007:%20Zod%20Validation%20and%20esbuild%20Bundling.md)** - Zod Validation
- **[ADR-008](docs/ADR-008:%20Sentry%20Error%20Tracking%20Integration.md)** - Sentry Integration
- **[ADR-009](docs/ADR-009:%20Timetable%20RBAC%20and%20Data%20Isolation.md)** - Timetable RBAC
- [ADR-010](docs/ADR-010:%20Migrating%20to%20Turso%20Cloud%20and%20Custom%20HTTP%20Connector.md) - Turso Cloud Migration
- **[ADR-011](docs/ADR-011:%20Implementing%20Security%20Headers%20with%20Talisman.md)** - Security Headers
- **[ADR-012](docs/ADR-012:%20Implementing%20GitHub%20Actions%20for%20CI.md)** - GitHub Actions CI/CD
- **[ADR-013](docs/ADR-013:%20Turso%20Database%20Sync%20Fix.md)** - Turso Cloud Synchronization Fix
- **[ADR-014](docs/ADR-014:%20One-Way%20Schedule%20Sync%20Architecture.md)** - One-Way Schedule Sync
- **[ADR-015](docs/ADR-015:%20GitHub%20Actions%20Fixes%20and%20Dependency%20Management.md)** - CI Pipeline Fixes
- **[ADR-016](docs/ADR-016:%20Non-Unique%20Group%20Naming%20and%20Coach-Based%20Identity.md)** - Non-Unique Group Names
- **[ADR-017](docs/ADR-017:%20Supporting%20Non-Unique%20Group%20Naming%20and%20Robust%20Timetable%20Synchronization.md)** - Supporting Non-Unique Group Names and Robust Timetable Synchronization
- **[ADR-018](docs/ADR-018:%20Google%20Sheets%20MCP%20Integration%20and%20Environment%20Configuration.md)** - Google Sheets MCP Integration
- **[ADR-019](docs/ADR-019:%20Fix%20Admin%20Setup%20and%20Sandbox%20Credentials.md)** - Fix Admin Setup and Sandbox Credentials
- **[ADR-020](docs/ADR-020:%20Structured%20Schedule%20Migration%20&%20Enhanced%20Sync%20Robustness.md)** - Structured Schedule Migration & Enhanced Sync Robustness
- **[ADR-021](docs/ADR-021:%20Agent%20Persistent%20Memory%20with%20Engram.md)** - Agent Persistent Memory with Engram
- **[ADR-022](docs/ADR-022:%20Mobile%20UI%20Refinements%20and%20Space%20Optimization.md)** - Mobile UI Refinements
- **[ADR-023](docs/ADR-023:%20Mobile%20Schedule%20Display%20Improvements.md)** - Mobile Schedule Pills
- **[ADR-024](docs/ADR-024:%20Vercel%20Production%20Cache%20Headers%20Fix.md)** - Vercel Production Cache Headers Fix
- **[ADR-025](docs/ADR-025:%20PWA%20Icon%20Fix%20for%20Android%20Home%20Screen.md)** - PWA Icon Fix for Android
- **[ADR-026](docs/ADR-026:%20Magic%20Draft%20Reliability%20and%20Vercel%20Dependency%20Alignment.md)** - Magic Draft reliability and Vercel dependency alignment
- **[ADR-027](docs/ADR-027:%20Auto-Sync%20Webhook%20and%20Cache%20Invalidation.md)** - Auto-Sync webhook architecture and cache invalidation
- **[ADR-029](docs/ADR-029:%20Supabase%20Coach%20Features.md)** - Supabase Coach Features, Family Dashboard, Unread Tracking, Quick Messages, Coach Reply, Admin Auditor
- **[MCP Configuration](docs/mcp-configuration.md)** - Google Sheets Agent Integration
- [PLAYBOOK](docs/PLAYBOOK.md) - Operations manual, Troubleshooting, Design Standards
- **[AGENTS](AGENTS.md)** - AI Agent Guidelines and "Guardian" roles
- **[TESTING](TESTING.md)** - Detailed testing strategy and pytest conventions
- **[API Reference](docs/API.md)** - API endpoints (coming soon)

## 🔒 Security

### Best Practices
1. ✅ Password hashing with werkzeug
2. ✅ Role-based access control (RBAC) at data layer
3. ✅ Session-based authentication
4. ✅ No PII leakage (role-based column filtering)
5. ✅ Email validation on all forms
6. ✅ Security Headers (X-Frame-Options, CSP, etc.) via Talisman

### For Production
1. Change `app.secret_key` to a random value
2. Use HTTPS (all free deployment options provide this)
3. Set `TEST_MODE = False` in app.py (line 36)
4. Use strong passwords
5. Regular backups (script in `scripts/backup.sh`)

## 🐛 Troubleshooting

### Emails Not Sending
```bash
# Check credentials
python3 -c "import smtplib; \
  s = smtplib.SMTP('smtp.gmail.com', 587); \
  s.starttls(); \
  s.login('your-email@gmail.com', 'your-app-password'); \
  print('✅ OK')"
```
- Verify `SENDER_EMAIL` and `SENDER_PASSWORD` are set
- Check Gmail spam folder
- Ensure 2FA is enabled and App Password was generated

### Database Errors
```bash
# Reset database
rm academy.db
python3 backend/app.py  # Will recreate DB automatically

# Or run migrations
python3 backend/migrate_schedules.py
```

### Port Already in Use
```bash
# Change port in app.py (line 773)
app.run(debug=True, host='0.0.0.0', port=5002)
```

See **[PLAYBOOK.md](docs/PLAYBOOK.md)** for more troubleshooting.

## 📈 Testing

The project follows a strict testing strategy defined in **[TESTING.md](TESTING.md)** and is automatically enforced via **GitHub Actions**.

### CI/CD Pipeline
- **Linting**: Automated character checks via `flake8`.
- **Formatting**: Automated consistency checks via `black`.
- **Testing**: Automated test execution via `pytest`.
- **Building**: Automated build validation via `esbuild`.

### Coverage Targets
- **CORE (Domain/RBAC)**: 100%
- **GLOBAL (Routes/UI)**: 80%

### Run Tests
```bash
# All tests
export PYTHONPATH=$PYTHONPATH:. && pytest tests/ -v

# Unit only
export PYTHONPATH=$PYTHONPATH:. && pytest tests/unit/ -v

# Integration + coverage
export PYTHONPATH=$PYTHONPATH:. && pytest tests/integration/ --cov=backend --cov-report=html
```

### Mocking Requirement
- ⚠️ **Always mock SMTP** in tests to avoid sending real emails.
- ⚠️ **Use `tmp_db` fixture** to avoid writing to `academy.db`.
### Test Credentials
```
Admin:  admin@tennis.com / admin123
Coach:  coach1@tennis.com / admin123
Family: family1@email.com / admin123
```

## 🚀 Deployment

### Production Architecture
- **Vercel** (primary, https://tennis-academy-six.vercel.app) — PG direct (pg8000) → Supabase REST API → Turso fallback. PWA-enabled.
- **Render** (backup, https://sf-tennis-kids.onrender.com) — Supabase PostgreSQL direct via pg8000 + IPv6, PWA-enabled

### Option 0: Docker (Local Development)

```bash
docker compose up --build
```

App runs at **http://localhost:5001** with hot reload via volume mounts.

### Option 1: Vercel (Fastest, recommended — Turso fallback)
1. Install Vercel CLI: `npm i -g vercel`
2. Login: `vercel login`
3. Set environment variables in Vercel dashboard:
   - `TURSO_URL` - Your Turso database URL
   - `TURSO_TOKEN` - Your Turso token
   - `SENDER_EMAIL` - Your Gmail address
   - `SENDER_PASSWORD` - Your Gmail app password
   - `GEMINI_API_KEY` - Gemini API key for Magic Draft
   - `SECRET_KEY` - Random string
   - `SYNC_API_KEY` - Shared secret for GAS webhook auth
   - `DATABASE_URL` - Supabase PostgreSQL connection string (optional — Vercel falls back to Turso due to IPv6)
   - `ENABLE_TALISMAN` - Set to `false` for Vercel/Serverless
4. Deploy:
```bash
vercel --prod
```

The app will be live at `https://your-project.vercel.app`

### Option 2: Render (Alternative — Supabase PostgreSQL via IPv6)
Render runs on Google Cloud with IPv6 support, so it connects directly to Supabase PostgreSQL.

1. Sign up at https://render.com
2. Connect your GitHub repository
3. Create Web Service (or use `render.yaml` in root)
4. Set environment variables:
   - `DATABASE_URL` - Supabase PostgreSQL connection string (primary for Render)
   - `TURSO_URL` - Your Turso database URL (fallback)
   - `TURSO_TOKEN` - Your Turso token
   - `SENDER_EMAIL` - Gmail address for notifications
   - `SENDER_PASSWORD` - Gmail app password
   - `SECRET_KEY` - Random string for sessions
   - `ENABLE_TALISMAN` - Set to `false` for Render
5. Deploy!

Render uses `wsgi.py` as the entry point with gunicorn.

### Option 2: PythonAnywhere
1. Sign up at https://www.pythonanywhere.com (free tier)
2. Upload your files
3. Create Web App → Flask
4. Set environment variables in WSGI config
5. Reload web app

### Option 3: Railway
1. Sign up at https://railway.app
2. Create new project
3. Deploy from GitHub or upload files
4. Set environment variables
5. Deploy!

## 📊 Tech Stack Details

### Backend: Flask
- Lightweight, easy to learn
- Perfect for small projects
- Built-in templating with Jinja2

### Database: SQLite
- No server needed
- File-based, portable
- Perfect for small teams
- Can handle up to 100K concurrent connections

### Frontend: Bootstrap 5
- Responsive grid system
- Mobile-first design
- Free, open-source
- No JavaScript framework needed

## 🎓 Learning Path

1. **Understand RBAC**: Read [ADR-001](docs/ADR-001-timetable-repository.md)
2. **Learn operations**: Read [PLAYBOOK.md](docs/PLAYBOOK.md)
3. **Explore code**:
   - `backend/app.py` - Main Flask app
   - `backend/repositories/timetable_repository.py` - RBAC logic
   - `backend/routes/timetables.py` - API endpoints
   - `frontend/templates/` - HTML templates

## 🤝 Contributing

Found a bug? Have a feature idea?
1. Create an issue
2. Describe the problem/feature
3. Submit a pull request

## 📝 License

MIT License - Free to use and modify!

## 👥 Support

- **Documentation**: [PLAYBOOK.md](docs/PLAYBOOK.md)
- **Issues**: Check GitHub Issues
- **Questions**: Create a discussion

---

## 📊 Project Status

```
✅ Core Features:  Complete
✅ RBAC:           Complete
✅ Email:          Complete
✅ Timetable Sync:   Complete (Google Sheets)
✅ Cloud Migration:  Complete (Turso Cloud)
✅ Premium UI:     Complete (centered layout)
✅ Modal System:   Complete (vanilla JS)
✅ Validation:     Complete (Zod + esbuild)
✅ Monitoring:     Complete (Sentry)
✅ CI/CD:          Complete (GitHub Actions)
✅ Tests:          Unit tests passing (20/20)
✅ Mobile UI:      Refined (v1.14.0)
✅ Coach Roster:    Schedule-based grouping (v1.15.0)
✅ Spreadsheet Sync: Continuation rows support (v1.15.0)
✅ Day Filter:      Server-side filtering on timetable & coach groups (v1.16.0)
✅ Theme Toggle:    V1/V2 color palette switcher (v1.16.0)
✅ Time Display:    Fixed AM/PM formatting bug (v1.16.0)
✅ UI Readability:  Enlarged day headers and time text on timetable & coach pages (v1.16.0)
✅ Docker Support:  Containerized deployment with docker-compose (v1.16.0)
✅ Vercel Caching:  Static asset CDN caching + template caching for cold starts (v1.16.0)
✅ Vercel Deploy:   Production deployment on Vercel (v1.16.0)
✅ PWA Icons:      Android home screen icon fix (v1.17.0)
✅ PWA Maskable:    Solid navy blue backgrounds for adaptive icons (v1.18.0)
✅ PWA Production:  manifest.json + sw.js + iOS meta tags, live on Vercel and Render (v1.25.0)
✅ Magic Draft:     Robust AI error handling and Vercel runtime dependency alignment (v1.19.0)
✅ Auto-Sync:       Google Sheets → Turso via installable GAS triggers + webhook (v1.20.0)
✅ Supabase Layer:  Coach groups, timetable, messaging, coach dashboard, admin dashboard via REST API (v1.23.0)
✅ Supabase PostgreSQL: Direct pg8000 connection with SSL + IPv6, PgBouncer port 6543, pool error handling (v1.25.0)
✅ REST API Fallback:  Supabase REST API for Vercel when PG direct is unreachable (HTTPS/IPv4), Turso last resort (v1.25.0)
⏸️ Admin CRUD:     Groups/users read-only — manage via Google Sheets (v1.20.0)
✅ Family Dashboard: Supabase enrollments + Supabase timetable (v1.24.0)
✅ Unread Tracking:  is_read per recipient, read/unread styling, Mark All Read, clickable alert card (v1.24.0)
✅ Admin Broadcast:  Supabase lesson-based messaging with Turso storage (v1.24.0)
✅ Message Acks:     ack_type/ack_at per recipient, OK/Received buttons, coach ack summary (v1.24.0)
✅ Quick Messages:   4 presets, 15-min rate limit, coach reply, family alerts widget (v1.24.0)
✅ Admin Auditor:    /admin/messages table, edit modal, soft delete, nav link (v1.24.0)
```

**Last Updated**: 2026-07-16
**Version**: 1.25.0
**Status**: Production Ready ✅

---

**Built with ❤️ for SF TENNIS KIDS CLUB** 🎾
