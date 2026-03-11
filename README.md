# SF TENNIS KIDS Club

A simple, free-tier communication platform for tennis clubs to connect administrators, coaches, and families via email notifications.

## 🎯 Features

### Role-Based Access Control (RBAC)
- **Admin**: Full access to manage users, groups, schedules, and send messages to all
- **Coach**: Manage assigned groups, send messages to their groups only
- **Family**: View messages for enrolled groups, see weekly schedules

### Weekly Timetables
- **View schedules by week** - Navigate between weeks with a clean 7x1 grid
- **Role-based filtering** - Admins see all, coaches see their groups, families see their kids' groups
- **Premium Centered Layout** - Elegant, focused experience using `max-w-7xl mx-auto` containers
- **Custom Modal System** - Reliable, vanilla JS interactions for all record creation (no Bootstrap JS dependencies)
- **Responsive design** - Optimized for mobile, tablet, and high-res desktops

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
- ✅ **Google Spreadsheet Integration** (Sync schedules automatically)
- ✅ Simple web interface for all roles
- ✅ 100% free (Python, Flask, Gmail SMTP)

## 🛠 Tech Stack

| Component | Technology | Cost |
|-----------|------------|------|
| Backend | Python 3.8+ + Flask | Free |
| Database | Turso Cloud (libSQL) | Free |
| Email | Python smtplib + Gmail | Free |
| Frontend | HTML5 + CSS3 + Bootstrap 5 | Free |
| Validation| **Zod** + esbuild | Free |
| Monitoring | **Sentry** | Free tier |
| Security | **flask-talisman** (Security Headers) | Free |
| CI/CD | GitHub Actions | Free |
| Deployment | PythonAnywhere / Render / Railway | Free tier available |

## 📦 Installation

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
6. Send Messages: Admin Panel → Send Message → Select recipients → Send
7. View Schedules: Dashboard → View Weekly Schedules
```

### Coach Workflow
```
1. Login with coach credentials
2. Dashboard → My Groups (view assigned groups)
3. Dashboard → Send Message (notify families)
4. Dashboard → View Weekly Schedules (see all sessions)
```

### Family Workflow
```
1. Login with family credentials
2. Dashboard → My Enrollments (see kids' groups)
3. Dashboard → View Weekly Schedules (see kids' schedules)
4. Dashboard → My Messages (receive notifications)
5. Email notifications arrive automatically
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
message_recipients(id, message_id, user_id, email_sent, sent_at)
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
Admin:  gelenmp@gmail.com / tennis2026
Coach:  rc@tennis.com / tennis2026
Family: family1@email.com / tennis2026
```

## 🚀 Deployment

### Option 1: PythonAnywhere (Recommended)
1. Sign up at https://www.pythonanywhere.com (free tier)
2. Upload your files
3. Create Web App → Flask
4. Set environment variables in WSGI config
5. Reload web app

### Option 2: Render
1. Sign up at https://render.com
2. Create Web Service → Connect GitHub
3. Set environment variables
4. Deploy!

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
🔜 Integration Tests: Coming soon
🔜 PDF Export:      Coming soon
🔜 Calendar View:   Coming soon
```

**Last Updated**: 2026-03-11  
**Version**: 1.12.1  
**Status**: Production Ready ✅

---

**Built with ❤️ for SF TENNIS KIDS CLUB** 🎾
