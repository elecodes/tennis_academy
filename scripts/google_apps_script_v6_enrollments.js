// SF TENNIS KIDS - ROBUST Turso Sync Script v6 (WITH ENROLLMENTS)
/* 
   ==========================================================================
   DEPLOYMENT INSTRUCTIONS:
   1. Open your Google Sheet.
   2. Go to Extensions > Apps Script.
   3. DELETE ALL existing code.
   4. PASTE THIS ENTIRE FILE.
   5. Click Deploy > New Deployment.
   6. Execute as: Me | Access: Anyone.
   7. Deploy and copy new URL to .env file.
   8. Restart server.
   ==========================================================================
*/

const TURSO_URL = "https://sfchat-gelenmp.aws-eu-west-1.turso.io"; 
const TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzIxMjExMDMsImlkIjoiMDE5Yzk5ZGQtZjAwMS03ZTgyLWFjMDMtZmIwMDg5ZTdhN2ZlIiwicmlkIjoiOTg4YzJhN2UtZDI3ZS00NmQ5LWE4OTQtYTBhYTIxYzliMzFmIn0.wo6KD364yHQu5wYq-XSudYjxagJQCV2vmWNdx0Q2DBPGm_euPJl6blkU-fS453_NEdO5dZUz--HsjBlJth0BBQ"; 

const DAYS_MAP = { 
  "monday": 0, "mon": 0, "tuesday": 1, "tue": 1, "wednesday": 2, "wed": 2, 
  "thursday": 3, "thu": 3, "friday": 4, "fri": 4, "saturday": 5, "sat": 5, "sunday": 6, "sun": 6
};

// Handle webhook POST requests
function doPost(e) {
  try {
    var contents = e.postData.contents;
    var payload = JSON.parse(contents);
    if (payload.action === "sync_all") {
      return createJsonResponse(syncAllData());
    }
    return createJsonResponse({ status: "success", info: "Action received" });
  } catch (error) {
    return createJsonResponse({ status: "error", message: error.toString() }, 400);
  }
}

// Test function - run this to test sync
function testSync() {
  try {
    var result = syncAllData();
    Logger.log("Sync Result: " + JSON.stringify(result));
    return result;
  } catch (error) {
    Logger.log("Error: " + error.toString());
    return { status: "error", message: error.toString() };
  }
}

function cleanTime(val) {
  if (!val) return "";
  
  if (val instanceof Date) {
    let hours = val.getHours();
    let minutes = val.getMinutes();
    let ampm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12;
    hours = hours ? hours : 12;
    minutes = minutes < 10 ? '0' + minutes : minutes;
    return hours + ':' + minutes + ' ' + ampm;
  }
  
  const timeStr = String(val).trim().toLowerCase();
  const match = timeStr.match(/(\d{1,2})[:.](\d{2})\s*(am|pm)?/);
  if (match) {
    let hours = parseInt(match[1]);
    let minutes = match[2];
    let ampm = match[3] || (hours >= 12 ? 'pm' : 'am');
    if (ampm === 'pm' && hours < 12) hours += 12;
    if (ampm === 'am' && hours === 12) hours = 0;
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
  let enrollmentsCreated = 0;
  let errors = [];

  // Clear existing schedules and members for full re-sync
  executeTursoSQL("DELETE FROM group_schedules;");
  executeTursoSQL("DELETE FROM group_members;");

  sheets.forEach(sheet => {
    const sheetName = sheet.getName().toLowerCase();
    const isDaySheet = Object.keys(DAYS_MAP).some(day => sheetName.includes(day));
    
    if (isDaySheet) {
      const colMap = getColumnMapping(sheet);
      const values = sheet.getDataRange().getValues();
      
      for (let i = 1; i < values.length; i++) {
        const rowData = values[i];
        const result = syncRowToTurso(sheet.getName(), colMap, rowData);
        if (result && result.status === "success") {
          totalProcessed++;
          if (result.enrollment) enrollmentsCreated++;
        }
        if (result && result.error) {
          errors.push(result.error);
        }
      }
    }
  });

  return { 
    status: "success", 
    version: "V6-ENROLLMENTS",
    rows_processed: totalProcessed,
    enrollments_created: enrollmentsCreated,
    errors: errors.length > 0 ? errors.slice(0, 5) : null
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
    else if (header.includes("email") || header.includes("parent")) map.email = i;
  });
  return map;
}

function syncRowToTurso(sheetName, colMap, data) {
  const time = cleanTime(data[colMap.time]);
  const kid = String(data[colMap.kid] || "").trim();
  const groupName = String(data[colMap.group] || "General").trim();
  const coachName = String(data[colMap.coach] || "").trim();
  const email = String(data[colMap.email] || "").trim();

  // Skip empty or header rows
  if (!time || time.toLowerCase() === "time" || time.includes("available")) {
    return { status: "ignored", reason: "empty" };
  }
  if (!kid && !groupName) {
    return { status: "ignored", reason: "no data" };
  }

  const dayOfWeek = getDayFromSheet(sheetName);
  const displaySchedule = getFullDayName(dayOfWeek) + " " + time;

  // 1. Find or create Coach
  let coachId = null;
  if (coachName) {
    const coachResult = executeBatch([{ 
      query: "SELECT id FROM users WHERE full_name LIKE ? AND role = 'coach' LIMIT 1", 
      args: ["%" + coachName + "%"] 
    }]);
    if (coachResult.status === "success" && coachResult.data.results[0].response.result.rows.length > 0) {
      coachId = coachResult.data.results[0].response.result.rows[0][0].value;
    }
  }

  const batch = [];
  
  // 2. Find existing group by name (regardless of coach for matching)
  let groupId = null;
  const groupLookup = executeBatch([{ 
    query: "SELECT id FROM groups WHERE name = ? LIMIT 1", 
    args: [groupName] 
  }]);
  if (groupLookup.status === "success" && groupLookup.data.results[0].response.result.rows.length > 0) {
    groupId = groupLookup.data.results[0].response.result.rows[0][0].value;
  }

  // 3. If group doesn't exist, create it
  if (!groupId) {
    const insertGroup = executeBatch([{
      query: "INSERT INTO groups (name, schedule, coach_id) VALUES (?, ?, ?)",
      args: [groupName, displaySchedule, coachId]
    }]);
    if (insertGroup.status === "success") {
      const newGroup = executeBatch([{ query: "SELECT last_insert_rowid()" }]);
      if (newGroup.status === "success") {
        groupId = newGroup.data.results[0].response.result.rows[0][0].value;
      }
    }
  } else {
    // Update existing group's schedule and coach
    batch.push({
      query: "UPDATE groups SET schedule = ?, coach_id = COALESCE(?, coach_id) WHERE id = ?",
      args: [displaySchedule, coachId, groupId]
    });
  }

  // 4. Create or find family user
  let familyId = null;
  if (email && email.includes("@")) {
    // Try to find existing user
    const userLookup = executeBatch([{ 
      query: "SELECT id FROM users WHERE email = ?", 
      args: [email] 
    }]);
    if (userLookup.status === "success" && userLookup.data.results[0].response.result.rows.length > 0) {
      familyId = userLookup.data.results[0].response.result.rows[0][0].value;
    } else {
      // Create new family user
      const familyName = kid ? kid + " Family" : "Family";
      const createUser = executeBatch([{
        query: "INSERT INTO users (email, full_name, role, password) VALUES (?, ?, 'family', 'temp_pass')",
        args: [email, familyName]
      }]);
      if (createUser.status === "success") {
        const newUser = executeBatch([{ query: "SELECT last_insert_rowid()" }]);
        if (newUser.status === "success") {
          familyId = newUser.data.results[0].response.result.rows[0][0].value;
        }
      }
    }
  }

  // 5. Create enrollment (group_members)
  if (groupId && familyId && kid) {
    const enrollmentResult = executeBatch([{
      query: "INSERT OR IGNORE INTO group_members (group_id, family_id, kid_name) VALUES (?, ?, ?)",
      args: [groupId, familyId, kid]
    }]);
    if (enrollmentResult.status === "success") {
      return { status: "success", enrollment: true, groupId: groupId, familyId: familyId };
    }
  }

  // 6. Add session to schedule (ONLY if coach and group exist - skip continuation rows)
  if (groupId && coachId) {
    batch.push({
      query: "INSERT INTO group_schedules (group_id, day_of_week, start_time, end_time, court) VALUES (?, ?, ?, ?, ?)",
      args: [groupId, dayOfWeek, time, time, "Court 1"]
    });
  }

  executeBatch(batch);
  return { status: "success", enrollment: false };
}

function getDayFromSheet(sheetName) {
  const name = sheetName.toLowerCase();
  for (let day in DAYS_MAP) if (name.includes(day)) return DAYS_MAP[day];
  return 0;
}

function getFullDayName(dayIndex) {
  return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][dayIndex] || "Monday";
}

function executeTursoSQL(sql, args = []) { 
  return executeBatch([{ query: sql, args: args }]); 
}

function executeBatch(statements) {
  const apiUrl = TURSO_URL.replace("libsql://", "https://") + "/v2/pipeline";
  const requests = statements.map(s => ({
    type: "execute", 
    stmt: { 
      sql: s.query, 
      args: (s.args || []).map(a => {
        if (a === null || a === undefined) return { type: "null" };
        if (typeof a === "number") return { type: "integer", value: String(a) };
        return { type: "text", value: String(a) };
      })
    }
  }));
  const payload = { requests: requests };
  const options = { 
    method: "post", 
    contentType: "application/json", 
    headers: { Authorization: "Bearer " + TURSO_TOKEN }, 
    payload: JSON.stringify(payload), 
    muteHttpExceptions: true 
  };
  try {
    const response = UrlFetchApp.fetch(apiUrl, options);
    const code = response.getResponseCode();
    if (code !== 200) return { status: "error", message: response.getContentText() };
    return { status: "success", data: JSON.parse(response.getContentText()) };
  } catch (e) { return { status: "error", message: e.toString() }; }
}

function createJsonResponse(data) { 
  return ContentService.createTextOutput(JSON.stringify(data)).setMimeType(ContentService.MimeType.JSON); 
}
