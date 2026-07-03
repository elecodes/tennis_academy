# 🎾 SF TENNIS KIDS CLUB - Operations Playbook

## Table of Contents
1. [Setup Initial](#setup-initial)
2. [Docker Setup](#docker-setup)
3. [Vercel Deployment & Caching](#vercel-deployment--caching)
4. [Daily Operations](#daily-operations)
5. [Design System](#design-system)
6. [Troubleshooting](#troubleshooting)
7. [Cloud Migration & Sync](#cloud-migration--sync)
8. [Backup & Recovery](#backup--recovery)
9. [Common Tasks](#common-tasks)
10. [Agentic Workflow & Memory](#agentic-workflow--memory)

---

## Setup Initial

### Quick Start with Docker

```bash
# 1. Clone project
cd tennis_academy

# 2. Set environment variables
export TURSO_URL=libsql://your-db.turso.io
export TURSO_TOKEN=your-token
export SENDER_EMAIL=your-email@gmail.com
export SENDER_PASSWORD=your-app-password

# 3. Run with Docker
docker compose up --build

# App available at http://localhost:5001
```

### First Time Setup (Manual)

```bash
# 1. Clone project
cd tennis_academy
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Set environment variables
export SENDER_EMAIL=your-email@gmail.com
export SENDER_PASSWORD=your-app-password
export SENTRY_DSN=your-sentry-dsn

# 4. Run app
python3 backend/app.py

# 5. Build Frontend Validations
npm install
npm run build:js

# 6. Visit setup page
# http://localhost:5001/setup
# Create admin account
```

### Create Test Data

```bash
# Option A: Use Sample Data (Automatic)
sqlite3 academy.db < backend/migrations/002_insert_sample_data.sql

# Option B: Manual via Admin Dashboard
# 1. Login as admin
# 2. Go to Users → Add User (create coaches)
# 3. Go to Groups → Add Group (create groups)
# 4. Go to Enrollments → Add Enrollment (assign kids)
```

---

## Docker Setup

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
- Environment variables set (Turso credentials, Gmail)

### Commands

```bash
# First time build and start
docker compose up --build

# Start (after first build)
docker compose up

# Start in background
docker compose up -d

# View logs
docker compose logs -f app

# Stop
docker compose down

# Rebuild after code changes
docker compose up --build

# Run tests inside container
docker compose run --rm app python -m pytest tests/ -v
```

### Volume Mounts
- `./backend:/app/backend` - Backend code hot-reloads
- `./frontend:/app/frontend` - Templates hot-reload

### Environment Variables
Set in `.env` file or export before running:
```bash
TURSO_URL=libsql://your-db.turso.io
TURSO_TOKEN=your-token
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
SECRET_KEY=your-secret-key
```

---

## Vercel Deployment & Caching

### Deploy to Vercel

```bash
# Install CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

### Required Environment Variables (Vercel Dashboard)
| Variable | Description |
|----------|-------------|
| `VERCEL` | Set to `1` to enable production mode (template caching) |
| `TURSO_URL` | Your Turso database URL (libsql://...) |
| `TURSO_TOKEN` | Your Turso auth token |
| `SENDER_EMAIL` | Gmail address for notifications |
| `SENDER_PASSWORD` | Gmail app password |
| `GEMINI_API_KEY` | Gemini API key used by Magic Draft |
| `SECRET_KEY` | Random string for Flask sessions |
| `SYNC_API_KEY` | Shared secret for GAS webhook auth |

### Caching Strategy

The app uses a 4-layer caching approach on Vercel:

| Layer | What | Cache Duration | How |
|-------|------|----------------|-----|
| **Static Assets** | CSS, JS, icons, fonts, manifest | 1 year (immutable) | `vercel.json` route headers |
| **Service Worker** | `sw.js` | 0 (always revalidate) | Separate route in `vercel.json` |
| **Templates** | Jinja2 templates | Per cold start | Disabled auto-reload when `VERCEL=1` |
| **API Responses** | GET routes (dashboard, timetable, etc.) | 2-5 min | `Cache-Control: private` header in app.py |

**Why this matters on Vercel:**
- Vercel is serverless — each request can trigger a cold start
- Static assets are served from Vercel's edge CDN (no cold start)
- Template caching eliminates file-watcher overhead on cold starts
- API response caching reduces Turso DB calls (2-5 min TTL)
- Service worker must always revalidate so PWA updates deploy immediately
- `private` cache ensures RBAC - each user/browser gets their own cached data

### Verifying Cache Headers

```bash
# Check static asset cache headers
curl -I https://your-app.vercel.app/static/css/main.css
# Should show: cache-control: public, max-age=31536000, immutable

# Check service worker cache headers
curl -I https://your-app.vercel.app/static/sw.js
# Should show: cache-control: public, max-age=0, must-revalidate
```

---

## Daily Operations

### Morning Routine (5 min)

```bash
# 1. Start the app
source venv/bin/activate
python3 backend/app.py

# 2. Check system health
curl http://localhost:5001/login  # Should return 200

# 3. View logs (check for errors)
# Look at terminal output for any errors

# 4. (Optional) Rebuild validations if schemas changed
npm run build:js
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

1. Login as ADMIN
2. Admin Dashboard → Groups
3. Click Edit Group
4. Update description or coach
5. Save

✅ To manage the actual session times/courts, use the **Schedules** page.

---

## Design System

### Premium UI Standards
As of Feb 2026, the application follows a **Premium Centered Layout** (`max-w-7xl mx-auto`).

1. **Typography**: Headings use `font-display` (Playfair Display), body uses `font-sans` (Inter).
2. **Colors**: 
   - **V1 (Default)**: Navy (`#1A237E`) + Orange accent (`#F57C00`) + Light background (`#F8F9FA`)
   - **V2 (Toggle)**: Deep Royal Blue (`#163E85`) + Golden Yellow (`#E6C200`) + Gray background (`#EEF0F5`)
   - Toggle via palette icon in header — persisted in localStorage
3. **Cards**: Use `.card-premium` for elevated, bordered containers.
4. **Modals**: Use the custom Vanilla JS system (see `ADR-002`).
5. **Mobile-First Optimization** (New Feb 2026):
   - **Timetables**: Use horizontal day selector and vertical group accordions on mobile viewports.
   - **Density**: Prefer clean headers; hide low-priority fields like "Capacity" on mobile to reclaim space for time/date.
   - **Typography**: Maintain large touch targets (min 48x48px) for all buttons and interactive elements.
   - **Schedule Display**: Use compact pills like "Mon 4pm", "Wed 5:30pm" instead of long strings.
   - **PWA Support**: App can be installed on mobile via "Add to Home Screen". Service worker caches offline access.
   - **Bottom Navigation**: Mobile users see fixed bottom nav bar with quick links (Home, Schedule, Groups/Kids, Message).
    - **Empty Days**: Days without scheduled lessons are hidden for coach/family to reduce clutter.
    - **Day Filter**: Schedule page has day filter buttons (Mon-Sun) to show only groups with lessons on that day.
    - **Readability**: Day headers use `text-lg` bold navy with thicker borders. Time text uses `text-base` for clear visibility.
    - **Coach Schedule**: Bold uppercase day names (`font-black text-base`) with larger time (`text-lg`) in schedule slot headers.

### Schedule Formatting Filters
The app provides Jinja2 filters for consistent schedule display:

| Filter | Purpose | Example |
|--------|---------|---------|
| `schedule_compact` | Parse schedule text to compact pills | `"Mon 4pm", "Wed 5:30pm"` |
| `format_time` | Convert time to 12h format (handles both 24h and 12h DB formats) | `"16:00"` → `"4pm"`, `"2:40:00pm"` → `"2:40pm"` |

Used in:
- `family_dashboard.html` - Enrollments section
- `admin/groups.html` - Groups table
- `coach/my_groups.html` - Coach's groups
- `coach_dashboard.html` - Active groups
- `family/enrollments.html` - Enrollment cards
- `timetable.html` - Session time cards

### Working with Modals
To add a new modal:
1. Wrap your form in `<div id="myModal" class="modal-overlay hidden">`.
2. Ensure the close button has `onclick="closeModal('myModal')'`.
3. Trigger it using `onclick="openModal('myModal')"` on your action button.

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

# 3. Check TEST_MODE in backend/app.py (line 36)
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

new_password = generate_password_hash('admin123')
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
# Edit backend/app.py
# app.run(debug=True, host='0.0.0.0', port=5002)
```

### Issue: Turso SSL Certificate Error
**Symptoms**: `[SSL: CERTIFICATE_VERIFY_FAILED]` when connecting to Turso.
**Solution**:
1. Ensure `certifi` is installed: `pip install certifi`.
2. The application automatically patches SSL context in `backend/database.py`.
3. If still failing, manually set:
   ```bash
   export SSL_CERT_FILE=$(python3 -m certifi)
   export REQUESTS_CA_BUNDLE=$(python3 -m certifi)
   ```

### Issue: Turso 505 / Handshake Error
**Symptoms**: `WSServerHandshakeError: 505` or `invalid response status`.
**Solution**:
1. This usually indicates an issue with the `libsql-client` WebSocket protocol.
2. The application uses a **Custom HTTP Connector** in `backend/database.py` to bypass this.
3. Ensure `TURSO_URL` starts with `https://` (or the connector will convert it).

### Issue: 500 Internal Server Error (Vercel)
**Symptoms**: After login or accessing protected pages, the server returns 500 Internal Server Error ONLY in production (Vercel).
**Solution**:
1. Check if the error is `AttributeError: 'str' object has no attribute 'headers'` in your logs.
2. This happens because decorators (like `@cache_response`) attempt to manipulate `.headers` on the returned template string.
3. Ensure the return value is wrapped in `make_response()` before altering headers: `response = make_response(f(*args, **kwargs))`.

### Issue: Magic Draft returns 500 in Vercel
**Symptoms**: Console shows `POST /api/draft-message` or `/admin/api/draft-message` with 500, and logs include `AI draft feature not available - genkit not installed`.
**Solution**:
1. Confirm Vercel installs runtime dependencies from `api/requirements.txt`.
2. Verify `genkit==0.5.1` and `genkit-plugin-google-genai==0.5.1` are present in that file.
3. Set `GEMINI_API_KEY` in Vercel Production environment variables.
4. Redeploy with "Clear build cache" to force a clean install.
5. If users are on stale frontend assets, keep both endpoints enabled: `/api/draft-message` and `/admin/api/draft-message`.

### Issue: PWA Icon Not Showing on Android Home Screen
**Symptoms**: Adding the app to Android home screen shows a generic letter instead of the app icon, or the icon has an ugly default grey/white background.
**Solution**:
1. **Verify icon format**: Run `file frontend/static/icons/icon-192.png` — it must say `PNG image data`, NOT `JPEG`.
2. **Validate manifest**: Check `manifest.json` uses separate entries for `"purpose": "any"` and `"purpose": "maskable"` (not combined `"any maskable"`).
3. **Solid Backgrounds for Maskable Icons**: Android adaptive icons *require* a solid background. If your source image is transparent, the OS will fill the background with a random color (usually grey or white). Ensure `icon-192-maskable.png` and `icon-512-maskable.png` have a solid brand color (e.g., `#163E85` Navy Blue) behind the logo.
4. **Check Vercel routing**: Ensure `vercel.json` does NOT have a `/static/:path*` route that could 404 on icon requests.
5. **Cache bust**: Bump the `?v=` query parameter in `base.html` on manifest and icon links. ALSO, increment the `CACHE_NAME` in `sw.js` (both in `frontend/static/sw.js` and `public/sw.js`) to force a fresh install of the service worker.
6. **User action**: Remove existing home screen shortcut, then re-add via browser menu (⋮ → "Add to Home Screen").

### Issue: CSP Blocking Resources
**Symptoms**: Images, fonts, or scripts fail to load; Sentry errors about "Content Security Policy".
**Solution**:
1. Check browser console for "Refused to load..." errors.
2. Update the `CSP` dictionary in `backend/app.py` to whitelist the required domain.
3. Common domains already whitelisted: `fonts.googleapis.com`, `cdn.tailwindcss.com`, `*.sentry.io`.

---

## 🤖 CI/CD & Automation

### GitHub Actions (CI)
The project uses GitHub Actions to ensure code quality on every push.

**Workflows include:**
1. **Python CI**: Checks `flake8` linting, `black` formatting, and runs `pytest`.
2. **Frontend CI**: Checks the `esbuild` build process.

### Troubleshooting CI Failures

#### ❌ Formatting Check Failed (`black`)
- **Fix**: Run `black .` locally, commit, and push.

#### ❌ Linting Check Failed (`flake8`)
- **Fix**: Run `flake8 .` locally, address reported issues, commit, and push.

#### ❌ Tests Failed (`pytest`)
- **Fix**: Run `pytest tests/` locally, debug the failing tests, fix them, commit, and push.

#### ❌ Build Failed (`npm run build:js`)
- **Fix**: Ensure `zod` and `esbuild` are working correctly locally by running `npm run build:js`.

---

## Cloud Migration & Sync

### Migrating Local Data to Turso
If you have data in `academy.db` and want to move it to the cloud:
1. Set `TURSO_URL` and `TURSO_TOKEN`.
2. Run the migration script:
   ```bash
   python3 scripts/migrate_to_cloud.py
   ```

### Google Spreadsheet Synchronization

The application syncs groups and schedules from a Google Sheet to the Turso database. There are two sync mechanisms:

- **Auto-Sync (v7, recommended)**: Edits propagate within seconds via installable GAS triggers
- **Manual Sync**: Admin dashboard button or GAS editor `testSync()`

---

#### 1. Auto-Sync Setup (GAS v7)

1. Open your Google Sheet → **Extensions** → **Apps Script**.
2. DELETE all existing code and paste the content of `scripts/google_apps_script_v7.js`.
3. Update `CONFIG.webhookUrl` to your deployed app URL.
4. Ensure `CONFIG.syncKey` matches `SYNC_API_KEY` in Vercel env vars.
5. Save (Ctrl+S).
6. In the editor, run `installOnEditTrigger()` once (creates the installable trigger for auto-sync on cell edits).
7. Run `installHourlyTrigger()` once (creates a safety-net hourly timer).
8. Run `testSync()` once to verify data syncs correctly.

**Auto-Sync Flow:**
```
User edits a cell in Sheets
        ↓
onSheetEdit (installable trigger) fires
        ↓
syncAllData() reads all sheets via getValues()
        ↓
cleanTime() handles Date objects + parses time strings
        ↓
Turso pipeline: DELETE old data → INSERT new data → cleanup orphans
        ↓
notifyFlask() POST to /api/webhook/sheets-sync with X-Sync-Key
        ↓
Flask records last_sync_at → cache adaptivity kicks in
        ↓
Next browser request gets fresh data (cache bypass + 10s TTL)
```

#### 2. Spreadsheet Format

- Each sheet tab = day name (e.g., `MONDAY`, `TUESDAY`, `WEDNESDAYS`, `THURSDAY`, `FRIDAY`, `SATURDAY`, `SUNDAY`).
- Columns (detected by header text):
  | Column | Header examples | Required |
  |--------|----------------|----------|
  | Time | `Time`, `Hora` | Yes |
  | Coach | `Coach`, `Entrenador` | Yes |
  | Group | `Group`, `Grupo` | Yes |
  | Kid Name | `Kid`, `Niño`, `Alumno` | Yes |
  | Parent Email | `Parent Email`, `Parent Mail` | No |
  | Parent Name | `Parent Name`, `Parent Nombre` | No |
  | Phone | `Phone`, `Teléfono`, `Celular` | No |
- Row 1 = headers. Rows 2+ = data.
- Blank rows are skipped automatically.

#### 3. Running Sync

- **Auto**: Every cell edit triggers `onSheetEdit` (debounced 30s).
- **Safety net**: Every hour via `syncAll` time-based trigger.
- **Manual (editor)**: Run `testSync()` from the GAS editor.

#### 4. Cache Invalidation

The app uses an adaptive cache strategy to ensure users see fresh data quickly:

| Layer | Behavior |
|-------|----------|
| **Flask API** | `@cache_response` sets `max-age=10` if sync <60s ago, else `max-age=60` |
| **Service Worker** | v10+ uses `{cache: 'no-cache'}` on timetable requests |
| **Vercel CDN** | Dynamic routes are not cached (serverless) |
| **Browser** | Navigation requests bypass HTTP cache via SW |

**Flow after a Sheets edit:**
1. GAS writes to Turso
2. GAS calls `/api/webhook/sheets-sync` → Flask sets `last_sync_at`
3. Flask returns `max-age=10` (10s TTL) for next 60s
4. SW fetches timetable bypassing HTTP cache (`{cache: 'no-cache'}`)
5. User sees fresh data within seconds

#### 5. Debugging Sync

- **Sync status**: `GET /api/debug/sync-status` (JSON with group/schedule counts, last sync time)
- **GAS logs**: View → Logs in the Apps Script editor
- **Flask logs**: Check Vercel deployment logs for `POST /api/webhook/sheets-sync`

#### 6. Support for Duplicate Group Names
As of version 1.12.1, the system supports multiple groups with the same name (e.g., "Private"), provided they have different coaches.
- **Identity**: A group is uniquely identified by `(name, coach)`.
- **Display**: The Admin Dashboard and Timetable clearly show the coach name next to the group name to avoid confusion.
- **Google Sheets**: Ensure that if you create multiple groups with the same name in the spreadsheet, they have distinct coach entries in the "Coach" column.

#### 7. Schedule Migration Utility
For transitioning legacy text-based schedules to structured records:
1. Run the migration script locally or on the server:
   ```bash
   python3 backend/migrate_schedules.py
   ```
2. This will parse the `schedule` column in the `groups` table and populate `group_schedules`.

#### 8. Google Sheets MCP Integration (AI Agents)
For AI agents (like Antigravity) to interact with schedules:
1.  **Configuration**: Defined in `mcp_config.json`.
2.  **Credentials**: Uses `GOOGLE_APPLICATION_CREDENTIALS` pointing to the service account JSON.
3.  **Troubleshooting**:
    -   If the server isn't appearing, verify the `args` in `mcp_config.json` use `uvx mcp-google-sheets@latest`.
    -   Ensure the `DRIVE_FOLDER_ID` is a clean ID, not a URL.
    -   **Bypass**: If the agent can't find the tool, use `uv run --with google-api-python-client --with google-auth script.py` for direct access.

#### 9. Direct Python Sync Script
For syncing data directly from Google Sheets without Apps Script:
```bash
python3 scripts/sync_from_sheets.py
```
This script:
- Connects directly to Google Sheets API
- Syncs schedules and sessions to Turso database
- Updates group schedule summaries automatically
- Creates/updates enrollments based on parent emails

---

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
python3 backend/app.py
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

### Add/Delete Sessions (Admin)

```
1. Login as ADMIN
2. Dashboard → View Weekly Schedules (Schedules page)
3. To Add:
   - Click "Add New Session"
   - Select group, day, time, and court
   - Click Save
4. To Delete:
   - Hover over a session in the grid
   - Click the red "x" icon
   - Confirm deletion
```

✅ Changes appear immediately for all users.

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
3. Group: Select your group (or specific schedule slot)
4. Subject: "Session Update"
5. Content: Your message
6. Send

✅ All families get email immediately
```

**Schedule-Specific Messaging (Admin)**: Admins can target messages to specific time slots like "Beginners — Mon 5:15pm" instead of the entire group. Select the desired slot from the dropdown when sending.

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
-- Note: '0' is Monday, '6' is Sunday
SELECT g.name, gs.day_of_week, gs.start_time, gs.end_time, gs.court
FROM group_schedules gs
JOIN groups g ON gs.group_id = g.id
WHERE gs.day_of_week >= 0 AND gs.day_of_week <= 6
ORDER BY gs.day_of_week, gs.start_time;

-- Messages sent
SELECT m.subject, u.full_name as from_coach, g.name as to_group, m.sent_at
FROM messages m
JOIN users u ON m.sender_id = u.id
LEFT JOIN groups g ON m.group_id = g.id
ORDER BY m.sent_at DESC
LIMIT 10;
```

---
## Working with AI Agents

The project uses a "Guardian" system to ensure security and quality.

### 🤖 Agent Roles
- **Developer Agent**: Implements features and fixes.
- **Testing Guardian**: Enforces the rules in `TESTING.md`.
- **Security Guardian**: Enforces the rules in `SECURITY.md`.

### 🎾 Invoking Skills
When working with AI agents, you can ask them to use specific skills:
- `RBACGuardian`: Checks route decorators and permissions.
- `EmailSafety`: Ensures SMTP is mocked in tests.
- `QualityTesting`: Checks coverage targets.

For more details, see **[AGENTS.md](AGENTS.md)**.

## 🆘 Troubleshooting

### ❌ ImportError: incompatible architecture (have 'arm64', need 'x86_64')
**Symptoms**: Pre-commit hooks (e.g., `black`, `flake8`) fail with an architecture mismatch error when committing.
**Cause**: Git is running in Intel mode (via Rosetta) while Python tools are native ARM64.
**Fix**: Use the native Apple Git located at `/usr/bin/git`.
- Permanently fix by updating your shell PATH to prioritize `/usr/bin` over `/usr/local/bin` (where Intel Git often resides).
- Or alias git: `alias git='/usr/bin/git'` in your `.zshrc`.

-----------------

## Contact & Support

- **Issue with app**: Create issue on GitHub
- **Email problem**: Check SENDER_EMAIL and SENDER_PASSWORD
- **Database corrupt**: Delete academy.db and reinitialize
- **Need help**: Check logs in terminal output

---

## Coach Dashboard (v1.15.0+)
Simplified coach experience - no family email exposure:

**Coach Actions:**
- Send Message to groups
- View Roster (student names by schedule slot)

**Group Cards Display:**
- Group name
- Schedule slots with enrolled students
- Students grouped by their specific time slot (e.g., Sat 11am shows all kids at that slot)

**My Groups Page (v1.15.0+):**
- Shows students organized by schedule slot
- Each slot shows the day/time with student names below
- Continuation rows from spreadsheet are properly synced (kids with same time appear together)

**Spreadsheet Sync (v1.15.0+):**
- Handles continuation rows (where time/coach/group columns are empty)
- Only enrolls rows with explicit group column filled
- Normalizes time formats to prevent duplicates

This ensures coaches can manage their groups without accessing family personal data.

---

## Supabase Integration (v1.22.0+)

The app uses Supabase (PostgreSQL) as a secondary read layer alongside Turso, synced from Google Sheets via GAS v7.

### Available Supabase Features

| Feature | Route | Description |
|---------|-------|-------------|
| Students | `GET /admin/students` | Student list from Supabase |
| Enrollments | `GET /admin/enrollments-supabase` | Enrollments joining students + lessons + seasons + coaches |
| Users | `GET /admin/users-supabase` | Unified view of Supabase coaches + students |
| Coach Groups | `GET /coach/my-groups-supabase` | Coach's lessons with student rosters |
| Timetable | `GET /timetable-supabase` | Weekly schedule from Supabase with RBAC |
| Send Message | `GET/POST /coach/send-message-supabase` | Email parents via Supabase (Magic Draft supported) |

### Dashboard Integration

**Admin Dashboard** shows:
- **Supabase Sync stat card**: lesson/coach/student counts alongside Turso stats
- **Supabase Lessons grid**: 9 cards showing title, type badge, coach, and time (between stats and Club Command Center)

**Coach Dashboard** (Supabase-first logic):
- Coaches with Supabase lessons see ONLY Supabase groups (Turso groups hidden)
- Coaches without Supabase data fall back to Turso groups
- This avoids duplicate cards and keeps the coach focused on the richer Supabase data

### Supabase URLs

- **Supabase Project**: `ypbwlpeighgpafocauzp.supabase.co`
- **API Endpoint**: `https://ypbwlpeighgpafocauzp.supabase.co/rest/v1`
- **Tables**: `coaches`, `lessons`, `students`, `student_lessons`, `seasons`

### Key Functions in `supabase_db.py`

| Function | Purpose |
|----------|---------|
| `fetch_lessons()` | All lessons ordered by day, time |
| `fetch_coaches()` | All coaches |
| `fetch_students()` | All students ordered by name |
| `fetch_seasons()` | All seasons ordered by name |
| `fetch_enrollments()` | Joined data: students + lessons + seasons + coaches |
| `fetch_supabase_users()` | Aggregated coach + student list for unified users page |
| `fetch_coach_groups(coach_name)` | Coach's lessons deduped by (day, time) with student rosters |
| `fetch_timetable(role, user_name)` | Weekly schedule dict compatible with `timetable.html` |
| `fetch_coach_lessons(coach_name)` | Flat list of coach's lessons for message form |
| `fetch_lesson_parents(lesson_id)` | Parent contacts via student_lessons → students |

### Keeping Supabase Alive

Supabase free tier pauses projects after 7 days of inactivity. GitHub Actions cron job `.github/workflows/keep-supabase-alive.yml` pings the REST API every 3 days to prevent this. Requires these **GitHub secrets**:

- `SUPABASE_URL` — `https://ypbwlpeighgpafocauzp.supabase.co/rest/v1`
- `SUPABASE_ANON_KEY` — your Supabase anon/public key

**Last Updated**: 2026-07-02
**Version**: 1.23.0