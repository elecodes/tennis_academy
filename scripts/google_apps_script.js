// SF TENNIS KIDS - Turso Sync Script (Multi-Sheet Version)
// 1. Open your Google Sheet.
// 2. Go to Extensions > Apps Script.
// 3. Delete any existing code and paste this.
// 4. Update TURSO_URL and TURSO_TOKEN below.
// 5. Run 'syncAllData' once to sync every sheet!

const TURSO_URL = "libsql://sfchat-gelenmp.aws-eu-west-1.turso.io"; 
const TURSO_TOKEN = "PASTE_YOUR_TOKEN_HERE"; 

const DAYS_MAP = { 
  "monday": 0, "mon": 0, 
  "tuesday": 1, "tue": 1, 
  "wednesday": 2, "wed": 2, 
  "thursday": 3, "thu": 3, 
  "friday": 4, "fri": 4, 
  "saturday": 5, "sat": 5, 
  "sunday": 6, "sun": 6 
};

function onSpreadsheetEdit(e) {
  if (!e || !e.source) return;
  const sheet = e.source.getActiveSheet();
  const row = e.range.getRow();
  if (row === 1) return;
  syncRowToTurso(sheet, row);
}

function syncAllData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheets = ss.getSheets();
  
  Logger.log("Starting full sync across " + sheets.length + " sheets...");
  
  // Ensure tables exist
  executeTursoSQL("CREATE TABLE IF NOT EXISTS group_schedules (id INTEGER PRIMARY KEY AUTOINCREMENT, group_id INTEGER NOT NULL, day_of_week INTEGER NOT NULL, start_time TEXT NOT NULL, end_time TEXT NOT NULL, court TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE);");

  sheets.forEach(sheet => {
    const sheetName = sheet.getName().toLowerCase();
    // Only sync sheets that seem to represent days or data
    if (Object.keys(DAYS_MAP).some(day => sheetName.includes(day)) || sheetName.includes("data")) {
      Logger.log("Syncing sheet: " + sheet.getName());
      const lastRow = sheet.getLastRow();
      for (let i = 2; i <= lastRow; i++) {
        syncRowToTurso(sheet, i);
      }
    }
  });
  Logger.log("Full sync complete!");
}

function syncRowToTurso(sheet, rowNum) {
  // Use getDisplayValue for the first column (Time) to avoid Date object issues
  const displayTime = sheet.getRange(rowNum, 1).getDisplayValue(); 
  const data = sheet.getRange(rowNum, 1, 1, 10).getValues()[0];
  
  const entry = {
    time: displayTime,
    coachName: String(data[1]).trim(),
    groupName: String(data[2]).trim(),
    kidName: String(data[3]).trim(),
    parentEmail: String(data[8]).trim()
  };

  // Skip empty rows
  if (!entry.groupName || entry.groupName === "" || entry.groupName === "Group") {
    // If it's literally named "Group", check if there's other info
    if (!entry.kidName) return;
  }

  const sheetName = sheet.getName();
  const dayOfWeek = getDayFromSheet(sheetName);
  const fullDay = getFullDayName(dayOfWeek);
  
  // Create a nice display schedule: "Monday 4:00 PM"
  const displaySchedule = fullDay + " " + displayTime;

  // 1. Ensure Family User exists
  const sqlUser = {
    query: "INSERT INTO users (email, full_name, role, password) SELECT ?, ?, 'family', 'temp_pass' WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = ?)",
    args: [entry.parentEmail, entry.kidName + " Family", entry.parentEmail]
  };

  // 2. Upsert Group (Update schedule/coach if name matches)
  const sqlGroup = {
    query: `INSERT INTO groups (name, schedule, coach_id) 
            VALUES (?, ?, (SELECT id FROM users WHERE full_name = ? AND role = 'coach' LIMIT 1)) 
            ON CONFLICT(name) DO UPDATE SET 
            schedule = excluded.schedule, 
            coach_id = excluded.coach_id`,
    args: [entry.groupName, displaySchedule, entry.coachName]
  };

  // 3. Enroll Student
  const sqlEnroll = {
    query: "INSERT INTO group_members (group_id, family_id, kid_name) SELECT g.id, u.id, ? FROM groups g, users u WHERE g.name = ? AND u.email = ? ON CONFLICT DO NOTHING",
    args: [entry.kidName, entry.groupName, entry.parentEmail]
  };

  // 4. Update Schedule
  // First clear existing schedules for this specific day/group
  const sqlCleanup = {
    query: "DELETE FROM group_schedules WHERE group_id IN (SELECT id FROM groups WHERE name = ?) AND day_of_week = ?",
    args: [entry.groupName, dayOfWeek]
  };

  const sqlSession = {
    query: "INSERT INTO group_schedules (group_id, day_of_week, start_time, end_time, court) SELECT id, ?, ?, ?, 'Court 1' FROM groups WHERE name = ?",
    args: [dayOfWeek, entry.time, entry.time, entry.groupName] // Note: end_time same as start if not range
  };

  executeBatch([sqlUser, sqlGroup, sqlEnroll, sqlCleanup, sqlSession]);
}

function getDayFromSheet(sheetName) {
  const name = sheetName.toLowerCase();
  for (let day in DAYS_MAP) {
    if (name.includes(day)) return DAYS_MAP[day];
  }
  return 0; // Default to Monday
}

function getFullDayName(dayIndex) {
  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  return days[dayIndex] || "Monday";
}

function executeTursoSQL(sql, args = []) {
  return executeBatch([{ query: sql, args: args }]);
}

function executeBatch(statements) {
  const cleanToken = TURSO_TOKEN.trim().replace(/^Bearer\s+/i, "");
  const apiUrl = TURSO_URL.replace("libsql://", "https://") + "/v2/pipeline";
  
  const payload = {
    requests: statements.map(s => ({
      type: "execute",
      stmt: { 
        sql: s.query, 
        args: s.args ? s.args.map(a => {
          if (a === null || a === undefined || a === "null") return { type: "null" };
          return { type: "text", value: String(a) };
        }) : [] 
      }
    }))
  };

  const options = {
    method: "post",
    contentType: "application/json",
    headers: { Authorization: "Bearer " + cleanToken },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  try {
    const response = UrlFetchApp.fetch(apiUrl, options);
    const code = response.getResponseCode();
    if (code !== 200) {
      Logger.log("ERROR: Turso API error (" + code + "): " + response.getContentText());
    } else {
      // Logger.log("Success: Batch executed.");
    }
  } catch (e) {
    Logger.log("ERROR: Fetch failed: " + e.toString());
  }
}

// --- WEBHOOK RECEIVER ---

function doPost(e) {
  Logger.log("Received POST request");
  
  try {
    const payload = JSON.parse(e.postData.contents);
    Logger.log("Payload: " + JSON.stringify(payload));
    
    if (payload.action === "update_kid") {
      return handleUpdateKid(payload);
    } else if (payload.action === "update_group") {
       return handleUpdateGroup(payload);
    } else {
      return createJsonResponse({ status: "error", message: "Unknown action" }, 400);
    }
  } catch (error) {
    Logger.log("Error parsing JSON: " + error.toString());
    return createJsonResponse({ status: "error", message: "Invalid JSON payload" }, 400);
  }
}

function createJsonResponse(data, statusCode = 200) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}

function handleUpdateKid(payload) {
  const { originalKidName, parentEmail, originalGroupName, newKidName, newParentEmail, newGroupName } = payload;
  
  if (!originalKidName) {
    return createJsonResponse({ status: "error", message: "originalKidName is required" }, 400);
  }

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheets = ss.getSheets();
  let updatedRows = 0;
  
  // We need to find the student. They could be in multiple days if they have multiple schedules.
  // We'll update them everywhere they appear.
  sheets.forEach(sheet => {
    const sheetName = sheet.getName().toLowerCase();
    if (Object.keys(DAYS_MAP).some(day => sheetName.includes(day)) || sheetName.includes("data")) {
      const data = sheet.getDataRange().getValues();
      
      for (let i = 1; i < data.length; i++) { // Skip header
        const rowKidName = String(data[i][3]).trim();
        const rowEmail = String(data[i][8]).trim();
        const rowGroupName = String(data[i][2]).trim();
        
        // Match on Name + (Email OR Group) to be safe, or just Name if we assume names are unique enough for now
        // Let's match strictly on Name and Email if provided, or Name and Group
        let match = false;
        if (originalKidName.toLowerCase() === rowKidName.toLowerCase()) {
          if (parentEmail && rowEmail.toLowerCase() === parentEmail.toLowerCase()) match = true;
          else if (originalGroupName && rowGroupName.toLowerCase() === originalGroupName.toLowerCase()) match = true;
          else if (!parentEmail && !originalGroupName) match = true; // Fallback if only name provided
        }

        if (match) {
           // Update cells (Sheet rows/cols are 1-indexed)
           if (newKidName) sheet.getRange(i + 1, 4).setValue(newKidName); // Column D
           if (newParentEmail) sheet.getRange(i + 1, 9).setValue(newParentEmail); // Column I
           if (newGroupName) sheet.getRange(i + 1, 3).setValue(newGroupName); // Column C
           
           SpreadsheetApp.flush(); // Make sure values are written before sync
           
           // Sync this row back to Turso so Turso reflects the NEW values
           syncRowToTurso(sheet, i + 1);
           updatedRows++;
        }
      }
    }
  });

  if (updatedRows > 0) {
    return createJsonResponse({ status: "success", message: `Updated and synced ${updatedRows} rows` });
  } else {
    return createJsonResponse({ status: "not_found", message: "Kid not found in spreadsheet" }, 404);
  }
}

function handleUpdateGroup(payload) {
  const { originalGroupName, newGroupName, newCoachName, newScheduleTime, dayOfWeek } = payload;
  
  if (!originalGroupName) {
    return createJsonResponse({ status: "error", message: "originalGroupName is required" }, 400);
  }

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let updatedRows = 0;
  let targetSheet = null;

  // If a specific day is provided and we are updating the schedule, find that sheet
  if (dayOfWeek) {
      const dayNameLower = dayOfWeek.toLowerCase();
      const sheets = ss.getSheets();
      targetSheet = sheets.find(s => s.getName().toLowerCase().includes(dayNameLower));
  }

  if (targetSheet) {
      // We are moving the group to a new time/day? Or just updating the time on the existing day.
      // For simplicity right now, let's just update the rows where group name matches.
      const data = targetSheet.getDataRange().getValues();
      for (let i = 1; i < data.length; i++) {
         if (String(data[i][2]).trim().toLowerCase() === originalGroupName.toLowerCase()) {
             if (newGroupName) targetSheet.getRange(i + 1, 3).setValue(newGroupName);
             if (newCoachName) targetSheet.getRange(i + 1, 2).setValue(newCoachName);
             if (newScheduleTime) targetSheet.getRange(i + 1, 1).setValue(newScheduleTime);
             
             SpreadsheetApp.flush();
             syncRowToTurso(targetSheet, i + 1);
             updatedRows++;
         }
      }
  } else {
      // Check all sheets
      const sheets = ss.getSheets();
      sheets.forEach(sheet => {
         const sheetName = sheet.getName().toLowerCase();
         if (Object.keys(DAYS_MAP).some(day => sheetName.includes(day)) || sheetName.includes("data")) {
            const data = sheet.getDataRange().getValues();
            for (let i = 1; i < data.length; i++) {
               if (String(data[i][2]).trim().toLowerCase() === originalGroupName.toLowerCase()) {
                   if (newGroupName) sheet.getRange(i + 1, 3).setValue(newGroupName);
                   if (newCoachName) sheet.getRange(i + 1, 2).setValue(newCoachName);
                   
                   SpreadsheetApp.flush();
                   syncRowToTurso(sheet, i + 1);
                   updatedRows++;
               }
            }
         }
      });
  }

  if (updatedRows > 0) {
    return createJsonResponse({ status: "success", message: `Updated and synced ${updatedRows} rows` });
  } else {
    return createJsonResponse({ status: "not_found", message: "Group not found in spreadsheet" }, 404);
  }
}
