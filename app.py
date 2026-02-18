"""
Tennis Kids Academy - Communication System
A simple, free-tier communication platform for tennis academies.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from datetime import datetime, timedelta
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'academy.db')

# Email configuration - Using Gmail SMTP (free)
# Set TEST_MODE = False to send emails to real family addresses.
TEST_MODE = False
REDIRECT_TARGET = 'gelenmp@gmail.com'

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'gelenmp@gmail.com')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD', 'jpss htxt sssz raqm')
REDIRECT_EMAILS_TO = REDIRECT_TARGET if TEST_MODE else None


def init_db():
    """Initialize the database with tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'coach', 'family')),
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Groups table (tennis groups like "Beginners Mon/Wed", "Advanced Tue/Thu")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            schedule TEXT NOT NULL,
            coach_id INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (coach_id) REFERENCES users (id)
        )
    ''')
    
    # Group memberships (families enrolled in groups)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            family_id INTEGER NOT NULL,
            kid_name TEXT NOT NULL,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups (id),
            FOREIGN KEY (family_id) REFERENCES users (id),
            UNIQUE(group_id, family_id, kid_name)
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            group_id INTEGER,
            message_type TEXT NOT NULL CHECK(message_type IN ('rain_cancellation', 'coach_delay', 'announcement', 'schedule_change')),
            subject TEXT NOT NULL,
            content TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_general INTEGER DEFAULT 0,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (group_id) REFERENCES groups (id)
        )
    ''')
    
    # Message recipients (tracking who received what)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS message_recipients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            email_sent INTEGER DEFAULT 0,
            sent_at TIMESTAMP,
            FOREIGN KEY (message_id) REFERENCES messages (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def send_email(to_email, subject, body):
    """Send email using SMTP."""
    if REDIRECT_EMAILS_TO:
        body = f"--- [TEST MODE] REDIRECTED FROM: {to_email} ---\n\n" + body
        to_email = REDIRECT_EMAILS_TO
    
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


# Decorators for role-based access
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def coach_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') not in ['admin', 'coach']:
            flash('Coach access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND is_active = 1', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            flash(f'Welcome, {user["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    user_id = session['user_id']
    role = session['role']
    
    if role == 'admin':
        # Admin sees everything
        stats = {
            'total_users': conn.execute('SELECT COUNT(*) FROM users WHERE role != "admin"').fetchone()[0],
            'total_groups': conn.execute('SELECT COUNT(*) FROM groups').fetchone()[0],
            'total_messages': conn.execute('SELECT COUNT(*) FROM messages').fetchone()[0],
            'recent_messages': conn.execute('''
                SELECT m.*, u.full_name as sender_name, g.name as group_name
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                LEFT JOIN groups g ON m.group_id = g.id
                ORDER BY m.sent_at DESC LIMIT 5
            ''').fetchall()
        }
        template = 'admin_dashboard.html'
        
    elif role == 'coach':
        # Coach sees their groups and messages
        my_groups = conn.execute('''
            SELECT g.*, COUNT(DISTINCT gm.family_id) as member_count
            FROM groups g
            LEFT JOIN group_members gm ON g.id = gm.group_id
            WHERE g.coach_id = ?
            GROUP BY g.id
        ''', (user_id,)).fetchall()
        
        # Refined visibility: 
        # 1. Messages they sent
        # 2. Messages sent to their groups
        # 3. Messages sent directly to them
        # 4. General announcements
        recent_messages = conn.execute('''
            SELECT DISTINCT m.*, m.sender_name, g.name as group_name
            FROM (
                SELECT m.*, u.full_name as sender_name
                FROM messages m
                JOIN users u ON m.sender_id = u.id
            ) m
            LEFT JOIN groups g ON m.group_id = g.id
            LEFT JOIN message_recipients mr ON m.id = mr.message_id
            WHERE m.sender_id = ? 
               OR m.group_id IN (SELECT id FROM groups WHERE coach_id = ?)
               OR mr.user_id = ?
               OR m.is_general = 1
            ORDER BY m.sent_at DESC LIMIT 10
        ''', (user_id, user_id, user_id)).fetchall()
        
        stats = {'my_groups': my_groups, 'recent_messages': recent_messages}
        template = 'coach_dashboard.html'
        
    else:  # family
        # Family sees their enrolled groups and messages
        my_enrollments = conn.execute('''
            SELECT g.*, gm.kid_name, u.full_name as coach_name
            FROM group_members gm
            JOIN groups g ON gm.group_id = g.id
            LEFT JOIN users u ON g.coach_id = u.id
            WHERE gm.family_id = ?
        ''', (user_id,)).fetchall()
        
        # Refined visibility:
        # 1. Messages sent to their groups
        # 2. Messages sent directly to them
        # 3. General announcements
        messages = conn.execute('''
            SELECT DISTINCT m.*, m.sender_name, g.name as group_name
            FROM (
                SELECT m.*, u.full_name as sender_name
                FROM messages m
                JOIN users u ON m.sender_id = u.id
            ) m
            LEFT JOIN groups g ON m.group_id = g.id
            LEFT JOIN message_recipients mr ON m.id = mr.message_id
            WHERE m.group_id IN (SELECT group_id FROM group_members WHERE family_id = ?)
               OR mr.user_id = ?
               OR m.is_general = 1
            ORDER BY m.sent_at DESC
        ''', (user_id, user_id)).fetchall()
        
        stats = {'my_enrollments': my_enrollments, 'messages': messages}
        template = 'family_dashboard.html'
    
    conn.close()
    return render_template(template, stats=stats)


# ==================== ADMIN ROUTES ====================

@app.route('/admin/users')
@admin_required
def admin_users():
    conn = get_db()
    users = conn.execute('''
        SELECT u.*, 
               (SELECT COUNT(*) FROM group_members WHERE family_id = u.id) as enrollments
        FROM users u WHERE u.role != 'admin'
        ORDER BY u.created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('admin/users.html', users=users)


@app.route('/admin/users/add', methods=['POST'])
@admin_required
def admin_add_user():
    email = request.form['email']
    full_name = request.form['full_name']
    role = request.form['role']
    phone = request.form.get('phone', '')
    password = request.form['password']
    
    conn = get_db()
    try:
        hashed_password = generate_password_hash(password)
        conn.execute('''
            INSERT INTO users (email, password, full_name, role, phone)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, hashed_password, full_name, role, phone))
        conn.commit()
        flash('User added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Email already exists.', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('admin_users'))


@app.route('/admin/groups')
@admin_required
def admin_groups():
    conn = get_db()
    groups = conn.execute('''
        SELECT g.*, u.full_name as coach_name,
               COUNT(DISTINCT gm.family_id) as member_count
        FROM groups g
        LEFT JOIN users u ON g.coach_id = u.id
        LEFT JOIN group_members gm ON g.id = gm.group_id
        GROUP BY g.id
        ORDER BY g.created_at DESC
    ''').fetchall()
    coaches = conn.execute("SELECT * FROM users WHERE role = 'coach'").fetchall()
    conn.close()
    return render_template('admin/groups.html', groups=groups, coaches=coaches)


@app.route('/admin/groups/add', methods=['POST'])
@admin_required
def admin_add_group():
    name = request.form['name']
    schedule = request.form['schedule']
    coach_id = request.form.get('coach_id') or None
    description = request.form.get('description', '')
    
    conn = get_db()
    conn.execute('''
        INSERT INTO groups (name, schedule, coach_id, description)
        VALUES (?, ?, ?, ?)
    ''', (name, schedule, coach_id, description))
    conn.commit()
    conn.close()
    
    flash('Group created successfully!', 'success')
    return redirect(url_for('admin_groups'))


@app.route('/admin/enrollments')
@admin_required
def admin_enrollments():
    conn = get_db()
    enrollments = conn.execute('''
        SELECT gm.*, g.name as group_name, u.full_name as family_name, u.email
        FROM group_members gm
        JOIN groups g ON gm.group_id = g.id
        JOIN users u ON gm.family_id = u.id
        ORDER BY g.name, u.full_name
    ''').fetchall()
    groups = conn.execute("SELECT * FROM groups").fetchall()
    families = conn.execute("SELECT * FROM users WHERE role = 'family'").fetchall()
    conn.close()
    return render_template('admin/enrollments.html', enrollments=enrollments, groups=groups, families=families)


@app.route('/admin/enrollments/add', methods=['POST'])
@admin_required
def admin_add_enrollment():
    group_id = request.form['group_id']
    family_id = request.form['family_id']
    kid_name = request.form['kid_name']
    
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO group_members (group_id, family_id, kid_name)
            VALUES (?, ?, ?)
        ''', (group_id, family_id, kid_name))
        conn.commit()
        flash('Enrollment added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('This kid is already enrolled in this group.', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('admin_enrollments'))


@app.route('/admin/send-message', methods=['GET', 'POST'])
@admin_required
def admin_send_message():
    conn = get_db()
    
    if request.method == 'POST':
        message_type = request.form['message_type']
        subject = request.form['subject']
        content = request.form['content']
        group_id = request.form.get('group_id')
        is_general = 1 if request.form.get('is_general') else 0
        
        # Insert message
        cursor = conn.execute('''
            INSERT INTO messages (sender_id, group_id, message_type, subject, content, is_general)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], group_id, message_type, subject, content, is_general))
        message_id = cursor.lastrowid
        
        # Determine recipients
        if is_general:
            # Send to all families
            recipients = conn.execute("SELECT * FROM users WHERE role = 'family' AND is_active = 1").fetchall()
        elif group_id:
            # Send to families in specific group
            recipients = conn.execute('''
                SELECT DISTINCT u.* FROM users u
                JOIN group_members gm ON u.id = gm.family_id
                WHERE gm.group_id = ? AND u.is_active = 1
            ''', (group_id,)).fetchall()
        else:
            recipients = []
        
        # Send emails and track
        email_body = f"""
Tennis Academy Notification

Type: {message_type.replace('_', ' ').title()}
Subject: {subject}

{content}

---
This message was sent from the Tennis Academy Communication System.
        """
        
        sent_count = 0
        for recipient in recipients:
            if send_email(recipient['email'], f"[Tennis Academy] {subject}", email_body):
                conn.execute('''
                    INSERT INTO message_recipients (message_id, user_id, email_sent, sent_at)
                    VALUES (?, ?, 1, CURRENT_TIMESTAMP)
                ''', (message_id, recipient['id']))
                sent_count += 1
            else:
                conn.execute('''
                    INSERT INTO message_recipients (message_id, user_id, email_sent)
                    VALUES (?, ?, 0)
                ''', (message_id, recipient['id']))
        
        conn.commit()
        flash(f'Message sent to {sent_count} families!', 'success')
        return redirect(url_for('dashboard'))
    
    groups = conn.execute("SELECT * FROM groups").fetchall()
    conn.close()
    return render_template('admin/send_message.html', groups=groups)


@app.route('/admin/test-email', methods=['POST'])
@admin_required
def admin_test_email():
    """Send a test email to verify SMTP configuration."""
    test_recipient = request.form.get('test_email')
    if not test_recipient:
        flash('Please provide a test email address.', 'warning')
        return redirect(url_for('dashboard'))
    
    subject = "Tennis Academy - Test Connection"
    body = f"This is a test email sent at {datetime.now()} to verify your SMTP settings are working correctly."
    
    # We bypass REDIRECT_EMAILS_TO here to test the specific address provided
    success = False
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = test_recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        success = True
    except Exception as e:
        flash(f"SMTP Error: {str(e)}", 'danger')
        print(f"Test Email Error: {e}")
    
    if success:
        flash(f'Test email successfully sent to {test_recipient}!', 'success')
    
    return redirect(url_for('dashboard'))


# ==================== COACH ROUTES ====================

@app.route('/coach/send-message', methods=['GET', 'POST'])
@coach_required
def coach_send_message():
    conn = get_db()
    coach_id = session['user_id']
    
    # Get coach's groups
    my_groups = conn.execute('SELECT * FROM groups WHERE coach_id = ?', (coach_id,)).fetchall()
    
    if request.method == 'POST':
        message_type = request.form['message_type']
        subject = request.form['subject']
        content = request.form['content']
        group_id = request.form['group_id']
        
        # Verify this group belongs to the coach
        group = conn.execute('SELECT * FROM groups WHERE id = ? AND coach_id = ?', 
                           (group_id, coach_id)).fetchone()
        if not group:
            flash('Invalid group selected.', 'danger')
            conn.close()
            return redirect(url_for('coach_send_message'))
        
        # Insert message
        cursor = conn.execute('''
            INSERT INTO messages (sender_id, group_id, message_type, subject, content, is_general)
            VALUES (?, ?, ?, ?, ?, 0)
        ''', (coach_id, group_id, message_type, subject, content))
        message_id = cursor.lastrowid
        
        # Get recipients
        recipients = conn.execute('''
            SELECT DISTINCT u.* FROM users u
            JOIN group_members gm ON u.id = gm.family_id
            WHERE gm.group_id = ? AND u.is_active = 1
        ''', (group_id,)).fetchall()
        
        # Send emails
        email_body = f"""
Tennis Academy Notification - From Coach {session['full_name']}

Type: {message_type.replace('_', ' ').title()}
Group: {group['name']}
Subject: {subject}

{content}

---
This message was sent from the Tennis Academy Communication System.
        """
        
        sent_count = 0
        for recipient in recipients:
            if send_email(recipient['email'], f"[Tennis Academy] {subject}", email_body):
                conn.execute('''
                    INSERT INTO message_recipients (message_id, user_id, email_sent, sent_at)
                    VALUES (?, ?, 1, CURRENT_TIMESTAMP)
                ''', (message_id, recipient['id']))
                sent_count += 1
            else:
                conn.execute('''
                    INSERT INTO message_recipients (message_id, user_id, email_sent)
                    VALUES (?, ?, 0)
                ''', (message_id, recipient['id']))
        
        conn.commit()
        flash(f'Message sent to {sent_count} families!', 'success')
        return redirect(url_for('dashboard'))
    
    conn.close()
    return render_template('coach/send_message.html', groups=my_groups)


@app.route('/coach/my-groups')
@coach_required
def coach_my_groups():
    conn = get_db()
    coach_id = session['user_id']
    
    groups = conn.execute('''
        SELECT g.*, COUNT(DISTINCT gm.family_id) as member_count
        FROM groups g
        LEFT JOIN group_members gm ON g.id = gm.group_id
        WHERE g.coach_id = ?
        GROUP BY g.id
    ''', (coach_id,)).fetchall()
    
    # Get members for each group
    group_members = {}
    for group in groups:
        members = conn.execute('''
            SELECT gm.kid_name, u.full_name as parent_name, u.email, u.phone
            FROM group_members gm
            JOIN users u ON gm.family_id = u.id
            WHERE gm.group_id = ?
        ''', (group['id'],)).fetchall()
        group_members[group['id']] = members
    
    conn.close()
    return render_template('coach/my_groups.html', groups=groups, group_members=group_members)


# ==================== FAMILY ROUTES ====================

@app.route('/family/my-messages')
@login_required
def family_messages():
    if session['role'] != 'family':
        return redirect(url_for('dashboard'))
    
    conn = get_db()
    user_id = session['user_id']
    
    # Get family's group IDs
    my_groups = conn.execute('SELECT group_id FROM group_members WHERE family_id = ?', (user_id,)).fetchall()
    my_group_ids = [g['group_id'] for g in my_groups]
    
    messages = []
    if my_group_ids:
        placeholders = ','.join('?' * len(my_group_ids))
        messages = conn.execute(f'''
            SELECT m.*, u.full_name as sender_name, g.name as group_name
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            LEFT JOIN groups g ON m.group_id = g.id
            WHERE m.group_id IN ({placeholders}) OR m.is_general = 1
            ORDER BY m.sent_at DESC
        ''', tuple(my_group_ids)).fetchall()
    
    conn.close()
    return render_template('family/messages.html', messages=messages)


@app.route('/family/my-enrollments')
@login_required
def family_enrollments():
    if session['role'] != 'family':
        return redirect(url_for('dashboard'))
    
    conn = get_db()
    user_id = session['user_id']
    
    enrollments = conn.execute('''
        SELECT g.*, gm.kid_name, u.full_name as coach_name
        FROM group_members gm
        JOIN groups g ON gm.group_id = g.id
        LEFT JOIN users u ON g.coach_id = u.id
        WHERE gm.family_id = ?
    ''', (user_id,)).fetchall()
    
    conn.close()
    return render_template('family/enrollments.html', enrollments=enrollments)


# ==================== SETUP ROUTE ====================

@app.route('/setup')
def setup():
    """Create admin user if no users exist."""
    conn = get_db()
    user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    conn.close()
    
    if user_count > 0:
        flash('Setup already completed.', 'info')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        
        conn = get_db()
        hashed_password = generate_password_hash(password)
        conn.execute('''
            INSERT INTO users (email, password, full_name, role)
            VALUES (?, ?, ?, 'admin')
        ''', (email, hashed_password, full_name))
        conn.commit()
        conn.close()
        
        flash('Admin account created! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('setup.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001)
