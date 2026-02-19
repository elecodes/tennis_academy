# Tennis Academy Communication System

A simple, free-tier communication platform for tennis academies to connect administrators, coaches, and families via email notifications.

## 🎯 Features

### Role-Based Access Control (RBAC)
- **Admin**: Full access to manage users, groups, schedules, and send messages to all
- **Coach**: Manage assigned groups, send messages to their groups only
- **Family**: View messages for enrolled groups, see weekly schedules

### Weekly Timetables
- **View schedules by week** - Navigate between weeks with a clean 7x1 grid
- **Role-based filtering** - Admins see all, coaches see their groups, families see their kids' groups
- **Admin Management** - Inline "Add/Delete Session" tools for rapid scheduling
- **No PII leaks** - Families never see other family emails or IDs
- **Responsive design** - Works on mobile (≥320px), tablet, desktop

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
- ✅ SQLite database (no external DB needed)
- ✅ Simple web interface for all roles
- ✅ 100% free (Python, Flask, Gmail SMTP)

## 🛠 Tech Stack

| Component | Technology | Cost |
|-----------|------------|------|
| Backend | Python 3.8+ + Flask | Free |
| Database | SQLite | Free |
| Email | Python smtplib + Gmail | Free |
| Frontend | HTML5 + Bootstrap 5 + Jinja2 | Free |
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
python -m venv venv

# Activate it:
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
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
```

On Windows:
```cmd
set SENDER_EMAIL=your-email@gmail.com
set SENDER_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

### 6. Run the Application

```bash
python app.py
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
groups(id, name, schedule, coach_id, description, created_at)

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

- **[ADR-001](docs/ADR-001-timetable-repository.md)** - Architecture Decision: Timetable Repository Pattern
- **[PLAYBOOK](docs/PLAYBOOK.md)** - Operations manual, troubleshooting, common tasks
- **[API Reference](docs/API.md)** - API endpoints (coming soon)

## 🔒 Security

### Best Practices
1. ✅ Password hashing with werkzeug
2. ✅ Role-based access control (RBAC) at data layer
3. ✅ Session-based authentication
4. ✅ No PII leakage (role-based column filtering)
5. ✅ Email validation on all forms

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
python app.py  # Will recreate DB automatically

# Or run migrations
python3 scripts/init_migrations.py
```

### Port Already in Use
```bash
# Change port in app.py (line 773)
app.run(debug=True, host='0.0.0.0', port=5002)
```

See **[PLAYBOOK.md](docs/PLAYBOOK.md)** for more troubleshooting.

## 📈 Testing

### Run Unit Tests
```bash
pytest tests/ -v

# With coverage
pytest tests/ --cov=repositories --cov=routes --cov-report=html
```

### Test Credentials
```
Admin:  admin@tennis.com / admin123
Coach:  coach1@tennis.com / password123
Family: family1@email.com / password123
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
   - `app.py` - Main Flask app
   - `repositories/timetable_repository.py` - RBAC logic
   - `routes/timetables.py` - API endpoints
   - `templates/` - HTML templates

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
✅ Timetables:     Complete (with RBAC)
✅ Tests:          Unit tests passing (13/13)
🔜 Integration Tests: Coming soon
🔜 PDF Export:      Coming soon
🔜 Calendar View:   Coming soon
```

**Last Updated**: 2026-02-18  
**Version**: 1.0.0  
**Status**: Production Ready ✅

---

**Built with ❤️ for Tennis Academies** 🎾