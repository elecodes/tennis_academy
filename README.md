# Tennis Academy Communication System

A simple, free-tier communication platform for tennis academies to connect administrators, coaches, and families via email notifications.

## Features

### Role-Based Access Control
- **Admin**: Full access to manage users, groups, enrollments, and send messages to all
- **Coach**: View assigned groups, send messages to their groups
- **Family**: View messages for their enrolled groups and general announcements

### Message Types
- Rain cancellations (urgent)
- Coach delays (urgent)
- General announcements
- Schedule changes

### Key Features
- Email notifications sent automatically to all relevant recipients
- Group-based messaging (coaches message only their groups)
- General announcements (admin can message all families)
- Simple web interface for all user roles
- SQLite database (no external database needed)

## Tech Stack (100% Free)

| Component | Technology |
|-----------|------------|
| Backend | Python + Flask |
| Database | SQLite (built-in) |
| Email | Python smtplib + Gmail |
| Frontend | HTML + Jinja2 templates |

## Installation

### 1. Clone/Download the Project

```bash
cd tennis_academy
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Email (Gmail)

To send emails, you need to set up a Gmail App Password:

1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Go to Security → App Passwords
4. Generate a new app password for "Mail"
5. Copy the 16-character password

Set environment variables:

**On Windows:**
```cmd
set SENDER_EMAIL=your-email@gmail.com
set SENDER_PASSWORD=your-app-password
```

**On Mac/Linux:**
```bash
export SENDER_EMAIL=your-email@gmail.com
export SENDER_PASSWORD=your-app-password
```

### 5. Run the Application

```bash
python app.py
```

The app will be available at: http://localhost:5000

## Initial Setup

1. Visit http://localhost:5000/setup
2. Create the admin account
3. Log in with the admin credentials
4. Start adding coaches, families, groups, and enrollments

## Usage Guide

### Admin Workflow

1. **Add Coaches**: Go to Users → Add User → Select "Coach" role
2. **Add Families**: Go to Users → Add User → Select "Family" role
3. **Create Groups**: Go to Groups → Add Group (e.g., "Beginners Mon/Wed 4PM")
4. **Assign Coach**: Select a coach when creating the group
5. **Enroll Kids**: Go to Enrollments → Add Enrollment (link family + kid to group)
6. **Send Messages**: Go to Send Message → Select type → Write message → Send

### Coach Workflow

1. Log in with coach credentials
2. View "My Groups" to see assigned groups and member lists
3. Click "Send Message" to notify families about delays, cancellations, etc.
4. Messages are automatically emailed to all families in the selected group

### Family Workflow

1. Log in with family credentials
2. View "My Enrollments" to see kids' groups and schedules
3. View "My Messages" to see all notifications
4. Receive emails for rain cancellations, coach delays, announcements

## Database Schema

### Users Table
- id, email, password, full_name, role (admin/coach/family), phone, is_active

### Groups Table
- id, name, schedule, coach_id, description

### Group Members Table
- id, group_id, family_id, kid_name

### Messages Table
- id, sender_id, group_id, message_type, subject, content, sent_at, is_general

### Message Recipients Table
- id, message_id, user_id, email_sent, sent_at

## Free Deployment Options

### Option 1: PythonAnywhere (Recommended for Beginners)
1. Sign up at pythonanywhere.com (free tier)
2. Upload your files
3. Create a web app with Flask
4. Set environment variables in WSGI config
5. Done!

### Option 2: Render
1. Sign up at render.com
2. Create a new Web Service
3. Connect your GitHub repo or upload files
4. Set environment variables
5. Deploy!

### Option 3: Railway
1. Sign up at railway.app
2. Create a new project
3. Deploy from GitHub
4. Set environment variables
5. Deploy!

## Customization Ideas

### Add SMS Notifications
- Integrate Twilio (free trial available)
- Add phone verification
- Send critical alerts via SMS

### Add Calendar Integration
- Export group schedules to iCal
- Google Calendar integration
- Automatic reminders

### Add Photo Gallery
- Coaches can share photos from sessions
- Families can view their kids' progress

### Add Attendance Tracking
- Mark attendance for each session
- View attendance history
- Notify families of missed sessions

## Security Notes

1. **Change the secret key** in production:
   ```python
   app.secret_key = 'your-random-secret-key-here'
   ```

2. **Use HTTPS** in production (all free deployment options provide this)

3. **Strong passwords** - enforce password complexity

4. **Rate limiting** - add Flask-Limiter for production

5. **Input validation** - already implemented but can be enhanced

## Troubleshooting

### Emails Not Sending
- Check Gmail app password is correct
- Verify `SENDER_EMAIL` and `SENDER_PASSWORD` environment variables
- Check spam folders
- Enable "Less secure app access" (not recommended) or use App Password

### Database Errors
- Delete `academy.db` to reset (loses all data)
- Or run `init_db()` again to recreate tables

### Port Already in Use
```bash
# Change port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

## License

MIT License - Free to use and modify!

## Support

For issues or questions, please create an issue or contact the developer.

---

**Built with Python + Flask for Tennis Academies** 🎾
