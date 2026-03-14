// SF TENNIS KIDS - FINAL ROBUST Turso Sync Script (V4 - REGEX TIME EXTRACTOR)
/* 
   ==========================================================================
   CRITICAL DEPLOYMENT INSTRUCTIONS (PLEASE FOLLOW EXACTLY):
   1. Open your Google Sheet.
   2. Go to Extensions > Apps Script.
   3. DELETE ALL existing code in the editor (Ctrl+A then Backspace).
   4. PASTE THIS ENTIRE FILE.
   5. Click the blue 'Deploy' button (top right) > 'New Deployment'.
   6. For 'Execute as', select 'Me'.
   7. For 'Who has access', select 'Anyone'.
   8. Click 'Deploy'.
   9. COPY the NEW 'Web App URL' and update it in your `.env` file.
   10. RESTART your server (Ctrl+C in terminal and run python3 backend/app.py).
   ==========================================================================
*/

const TURSO_URL = "https://sfchat-gelenmp.aws-eu-west-1.turso.io"; 
const TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzIxMjExMDMsImlkIjoiMDE5Yzk5ZGQtZjAwMS03ZTgyLWFjMDMtZmIwMDg5ZTdhN2ZlIiwicmlkIjoiOTg4YzJhN2UtZDI3ZS00NmQ5LWE4OTQtYTBhYTIxYzliMzFmIn0.wo6KD364yHQu5wYq-XSudYjxagJQCV2vmWNdx0Q2DBPGm_euPJl6blkU-fS453_NEdO5dZUz--HsjBlJth0BBQ"; 

const DAYS_MAP = { 
  "monday": 0, "mon": 0, "tuesday": 1, "tue": 1, "wednesday": 2, "wed": 2, 
  "thursday": 3, "thu": 3, "friday": 4, "fri": 4, "saturday": 5, "sat": 5, "sunday": 6, "sun": 6
};

function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents);
    if (payload.action === "sync_all") {
       return createJsonResponse(syncAllData());
    }
    return createJsonResponse({ status: "success", info: "Action received" });
  } catch (error) {
    return createJsonResponse({ status: "error", message: error.toString() }, 400);
  }
}

/**
 * Super-robust time extractor.
 * Converts any value (Date or String) into clean "h:mm am/pm" format.
 */
function cleanTime(val) {
  if (!val) return "";
  
  // If it's a Date object, extract parts directly
  if (val instanceof Date) {
    let hours = val.getHours();
    let minutes = val.getMinutes();
    let ampm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12;
    hours = hours ? hours : 12;
    minutes = minutes < 10 ? '0' + minutes : minutes;
    return hours + ':' + minutes + ' ' + ampm;
  }
  
  // If it's a string, use regex to find time pattern (e.g. 10:30 am or 16:30)
  const timeStr = String(val).trim().toLowerCase();
  const match = timeStr.match(/(\d{1,2})[:.](\d{2})\s*(am|pm)?/);
  if (match) {
    let hours = parseInt(match[1]);
    let minutes = match[2];
    let ampm = match[3] || (hours >= 12 ? 'pm' : 'am');
    if (ampm === 'pm' && hours < 12) hours += 12;
    if (ampm === 'am' && hours === 12) hours = 0;
    
    // Format back to clean 12h string
    let h12 = hours % 12 || 12;
    let finalAmpm = hours >= 12 ? 'pm' : 'am';
    return h12 + ':' + minutes + ' ' + finalAmpm;
  }
  
  return "";
}

function syncAllData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheets = ss.getSheets();
  let totalProcessed = 0;

  // Clear existing schedules for full re-sync
  executeTursoSQL("DELETE FROM group_schedules;");

  sheets.forEach(sheet => {
    const sheetName = sheet.getName().toLowerCase();
    const isDaySheet = Object.keys(DAYS_MAP).some(day => sheetName.includes(day));
    
    if (isDaySheet) {
      const colMap = getColumnMapping(sheet);
      // Use getValues() for raw access, then clean it manually
      const values = sheet.getDataRange().getValues();
      
      for (let i = 1; i < values.length; i++) {
        const rowData = values[i];
        const result = syncRowToTurso(sheet, i + 1, colMap, rowData);
        if (result && result.status === "success") totalProcessed++;
      }
    }
  });

  return { 
    status: "success", 
    version: "V5-SUPER-CLEAN",
    rows_processed: totalProcessed 
  };
}

function getColumnMapping(sheet) {
  const headers = sheet.getRange(1, 1, 1, Math.max(sheet.getLastColumn(), 10)).getDisplayValues()[0];
  const map = { time: 0, coach: 1, group: 2, kid: 3, email: 8 };
  headers.forEach((h, i) => {
    const header = String(h).toLowerCase();
    if (header.includes("time")) map.time = i;
    else if (header.includes("coach")) map.coach = i;
    else if (header.includes("group")) map.group = i;
    else if (header.includes("kid")) map.kid = i;
    else if (header.includes("email")) map.email = i;
  });
  return map;
}

function syncRowToTurso(sheet, rowNum, colMap, data) {
  const time = cleanTime(data[colMap.time]);
  const kid = String(data[colMap.kid]).trim();
  const group = String(data[colMap.group]).trim();
  const coachName = String(data[colMap.coach]).trim();
  const email = String(data[colMap.email]).trim();

  // Skip headers or obviously empty rows
  if (!time || time.toLowerCase() === "time" || time.includes("available")) return { status: "ignored" };
  if (!kid && (!group || group === "Group" || group === "")) return { status: "ignored" };

  const dayOfWeek = getDayFromSheet(sheet.getName());
  const displaySchedule = getFullDayName(dayOfWeek) + " " + time;

  // 1. Resolve Coach
  let coachId = null;
  const coachLookup = executeBatch([{ query: "SELECT id FROM users WHERE full_name = ? AND role = 'coach' LIMIT 1", args: [coachName] }]);
  if (coachLookup.status === "success" && coachLookup.data.results[0].response.result.rows.length > 0) {
    coachId = coachLookup.data.results[0].response.result.rows[0][0].value;
  }

  const batch = [];
  
  // 2. Upsert Group
  batch.push({
    query: "INSERT INTO groups (name, schedule, coach_id) VALUES (?, ?, ?) ON CONFLICT(name, coach_id) DO UPDATE SET schedule = excluded.schedule",
    args: [group || "General Group", displaySchedule, coachId]
  });

  // 3. User & Enrollment
  if (email && email.includes("@")) {
    batch.push({
      query: "INSERT INTO users (email, full_name, role, password) SELECT ?, ?, 'family', 'temp_pass' WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = ?)",
      args: [email, (kid || "Student") + " Family", email]
    });
    batch.push({
      query: `INSERT INTO group_members (group_id, family_id, kid_name) 
              SELECT g.id, u.id, ? FROM groups g, users u 
              WHERE g.name = ? AND (g.coach_id = ? OR (g.coach_id IS NULL AND ? IS NULL)) AND u.email = ? 
              ON CONFLICT DO NOTHING`,
      args: [kid, group || "General Group", coachId, coachId, email]
    });
  }

  // 4. Session Schedule
  batch.push({
    query: `INSERT INTO group_schedules (group_id, day_of_week, start_time, end_time, court) 
            SELECT id, ?, ?, ?, 'Court 1' FROM groups 
            WHERE name = ? AND (coach_id = ? OR (coach_id IS NULL AND ? IS NULL))`,
    args: [dayOfWeek, time, time, group || "General Group", coachId, coachId]
  });

  return executeBatch(batch);
}

function getDayFromSheet(sheetName) {
  const name = sheetName.toLowerCase();
  for (let day in DAYS_MAP) if (name.includes(day)) return DAYS_MAP[day];
  return 0;
}

function getFullDayName(dayIndex) {
  return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][dayIndex] || "Monday";
}

function executeTursoSQL(sql, args = []) { return executeBatch([{ query: sql, args: args }]); }

function executeBatch(statements) {
  const apiUrl = TURSO_URL.replace("libsql://", "https://") + "/v2/pipeline";
  const payload = { requests: statements.map(s => ({ type: "execute", stmt: { 
    sql: s.query, 
    args: s.args ? s.args.map(a => (a === null || a === undefined) ? { type: "null" } : { type: "text", value: String(a) }) : [] 
  }})) };
  const options = { method: "post", contentType: "application/json", headers: { Authorization: "Bearer " + TURSO_TOKEN }, payload: JSON.stringify(payload), muteHttpExceptions: true };
  try {
    const response = UrlFetchApp.fetch(apiUrl, options);
    const code = response.getResponseCode();
    if (code !== 200) return { status: "error", message: response.getContentText() };
    return { status: "success", data: JSON.parse(response.getContentText()) };
  } catch (e) { return { status: "error", message: e.toString() }; }
}

function createJsonResponse(data) { return ContentService.createTextOutput(JSON.stringify(data)).setMimeType(ContentService.MimeType.JSON); }
