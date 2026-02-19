# 🎾 Tennis Academy - Operations Playbook

## Table of Contents
1. [Setup Initial](#setup-initial)
2. [Daily Operations](#daily-operations)
3. [Troubleshooting](#troubleshooting)
4. [Backup & Recovery](#backup--recovery)
5. [Common Tasks](#common-tasks)

---

## Setup Initial

### First Time Setup

```bash
# 1. Clone project
cd tennis_academy
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
export SENDER_EMAIL=your-email@gmail.com
export SENDER_PASSWORD=your-app-password

# 4. Run app
python app.py

# 5. Visit setup page
# http://localhost:5001/setup
# Create admin account
```

### Create Test Data

```bash
# Option A: Use Sample Data (Automatic)
sqlite3 academy.db < migrations/002_insert_sample_data.sql

# Option B: Manual via Admin Dashboard
# 1. Login as admin
# 2. Go to Users → Add User (create coaches)
# 3. Go to Groups → Add Group (create groups)
# 4. Go to Enrollments → Add Enrollment (assign kids)
```

---

## Daily Operations

### Morning Routine (5 min)

```bash
# 1. Start the app
source venv/bin/activate
python app.py

# 2. Check system health
curl http://localhost:5001/login  # Should return 200

# 3. View logs (check for errors)
# Look at terminal output for any errors
```

### Send Weekly Schedule Notification

```
1. Login as ADMIN
2. Dashboard → Send Message
3. Select Message Type: "announcement"
4. Select Target: "General" (all families)
5. Subject: "Weekly Schedule Reminder"
6. Content: Copy-paste from Google Docs
7. Click Send

✅ All families get email automatically
```

### Handle Rain Cancellation (Urgent)

```
1. Login as COACH whose group is affected
2. Dashboard → Send Message
3. Select Message Type: "rain_cancellation"
4. Select Group: Your affected group
5. Subject: "Session Cancelled - Rain"
6. Content: "Tuesday 4PM session cancelled due to rain. See you Wednesday!"
7. Click Send

✅ All families in that group get email within seconds
```

### Update Group Schedule

```
1. Login as ADMIN
2. Admin Dashboard → Groups
3. Click Edit Group
4. Update "schedule" field
5. Save

⚠️ NOTE: Currently schedule is a TEXT field
     Plan to migrate to `group_schedules` table next iteration
```

---

## Troubleshooting

### Issue: Emails Not Sending

**Symptoms**: Message sent, but families didn't receive email

**Solution**:
```bash
# 1. Check environment variables
echo $SENDER_EMAIL
echo $SENDER_PASSWORD

# 2. Test Gmail credentials
python3 << 'EOF'
import smtplib
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("your-email@gmail.com", "your-app-password")
    print("✅ Gmail credentials OK")
    server.quit()
except Exception as e:
    print(f"❌ Error: {e}")
EOF

# 3. Check TEST_MODE in app.py (line 36)
# If TEST_MODE = True, emails go to REDIRECT_TARGET instead

# 4. Check spam folder (Gmail filters aggressively)
```

### Issue: Login Not Working

**Symptoms**: "Invalid email or password" even with correct credentials

**Solution**:
```bash
# 1. Verify user exists
sqlite3 academy.db "SELECT email, role FROM users WHERE email='admin@tennis.com';"

# 2. Reset password
python3 << 'EOF'
import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('academy.db')
cursor = conn.cursor()

new_password = generate_password_hash('newpassword123')
cursor.execute('UPDATE users SET password=? WHERE email=?', 
               (new_password, 'admin@tennis.com'))

conn.commit()
conn.close()
print("✅ Password reset. New password: newpassword123")
EOF
```

### Issue: Database Locked

**Symptoms**: "database is locked" error

**Solution**:
```bash
# 1. Restart Flask app
# 2. Close any open DB connections (SQLite Browser, etc.)
# 3. Delete academy.db and reinitialize (if non-production)

# Check for locks
lsof | grep academy.db  # Mac/Linux

# Kill the process
kill -9 <PID>
```

### Issue: Port 5001 Already in Use

**Symptoms**: "Address already in use" error

**Solution**:
```bash
# Option A: Kill existing process
lsof -ti:5001 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :5001   # Windows

# Option B: Use different port
# Edit app.py line 773:
# app.run(debug=True, host='0.0.0.0', port=5002)
```

---

## Backup & Recovery

### Daily Backup Script

```bash
#!/bin/bash
# Save as: scripts/backup.sh

BACKUP_DIR="backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)

mkdir -p $BACKUP_DIR
cp academy.db $BACKUP_DIR/academy_$DATE.db

echo "✅ Backup created: $BACKUP_DIR/academy_$DATE.db"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "academy_*.db" -mtime +7 -delete
```

**Usage**:
```bash
chmod +x scripts/backup.sh
./scripts/backup.sh  # Creates backup
```

### Restore from Backup

```bash
# 1. List backups
ls -la backups/

# 2. Restore
cp backups/academy_2026-02-18_10-30-45.db academy.db

# 3. Restart app
python app.py
```

### Export Data to CSV

```bash
# Export users
sqlite3 academy.db ".mode csv" ".headers on" "SELECT * FROM users;" > users.csv

# Export groups
sqlite3 academy.db ".mode csv" ".headers on" "SELECT * FROM groups;" > groups.csv

# Export enrollments
sqlite3 academy.db ".mode csv" ".headers on" \
  "SELECT g.name as group, u.full_name as family, gm.kid_name 
   FROM group_members gm
   JOIN groups g ON gm.group_id = g.id
   JOIN users u ON gm.family_id = u.id;" > enrollments.csv
```

---

## Common Tasks

### Add New Coach

```
1. Login as ADMIN
2. Admin Dashboard → Users → Add User
3. Fill:
   - Email: coach2@tennis.com
   - Name: Juan García
   - Role: Coach
   - Phone: +34 912 345 678
4. Generate temp password
5. Send to coach via WhatsApp/email
6. Coach logs in and changes password
```

### Create New Group

```
1. Login as ADMIN
2. Admin Dashboard → Groups → Add Group
3. Fill:
   - Name: U-14 Advanced
   - Schedule: Mon/Wed 5PM, Sat 10AM
   - Coach: Select coach
   - Description: Advanced competitive group
4. Save
```

### Enroll Kid in Group

```
1. Login as ADMIN
2. Admin Dashboard → Enrollments → Add Enrollment
3. Fill:
   - Group: Select group
   - Family: Select family
   - Kid Name: Sofia García
4. Save
```

### View Weekly Schedule (as Family)

```
1. Login as family (family1@email.com / password123)
2. Dashboard → View Weekly Schedules
3. See all groups kid is enrolled in
4. See all sessions for that week
5. Print or share with family
```

### Send Message to Group

```
As COACH:
1. Dashboard → Send Message
2. Message Type: announcement (or rain_cancellation, coach_delay)
3. Group: Your group
4. Subject: "Session Update"
5. Content: Your message
6. Send

✅ All families get email immediately
```

---

## Database Schema Quick Reference

```sql
-- Users
SELECT * FROM users WHERE role='admin';      -- Admins
SELECT * FROM users WHERE role='coach';      -- Coaches
SELECT * FROM users WHERE role='family';     -- Families

-- Groups & Kids
SELECT g.name, u.full_name as coach, COUNT(DISTINCT gm.family_id) as families
FROM groups g
LEFT JOIN users u ON g.coach_id = u.id
LEFT JOIN group_members gm ON g.id = gm.group_id
GROUP BY g.id;

-- Schedule for week of 2026-02-16 (Monday)
SELECT g.name, gs.day_of_week, gs.start_time, gs.end_time, gs.court
FROM group_schedules gs
JOIN groups g ON gs.group_id = g.id
WHERE date('2026-02-16', '+' || gs.day_of_week || ' days') 
  BETWEEN '2026-02-16' AND '2026-02-22'
ORDER BY day_of_week, start_time;

-- Messages sent
SELECT m.subject, u.full_name as from_coach, g.name as to_group, m.sent_at
FROM messages m
JOIN users u ON m.sender_id = u.id
LEFT JOIN groups g ON m.group_id = g.id
ORDER BY m.sent_at DESC
LIMIT 10;
```

---

## Contact & Support

- **Issue with app**: Create issue on GitHub
- **Email problem**: Check SENDER_EMAIL and SENDER_PASSWORD
- **Database corrupt**: Delete academy.db and reinitialize
- **Need help**: Check logs in terminal output

---

**Last Updated**: 2026-02-18
**Version**: 1.0