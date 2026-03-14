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
  "sunday": 6, "sun": 6,
  "schedule": 0, "master": 0 // Added common defaults
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

  // CRITICAL: Clear all schedules before full sync to allow multiple sessions per day/group
  executeTursoSQL("DELETE FROM group_schedules;");

  let totalUpdated = 0;
  sheets.forEach(sheet => {
    const sheetName = sheet.getName().toLowerCase();
    const isDaySheet = Object.keys(DAYS_MAP).some(day => sheetName.includes(day));
    const isDataSheet = sheetName.includes("data");

    if (isDaySheet || isDataSheet) {
      Logger.log("Scanning sheet for data: " + sheet.getName());
      const lastRow = sheet.getLastRow();
      
      if (lastRow < 2) {
        Logger.log("Skipping empty sheet: " + sheet.getName());
        return;
      }

      for (let i = 2; i <= lastRow; i++) {
        const result = syncRowToTurso(sheet, i, true);
        if (result.status === "success") {
          totalUpdated++;
        }
      }
    } else {
      Logger.log("Skipping non-schedule sheet: " + sheet.getName());
    }
  });
  Logger.log("Full sync complete! Processed " + totalUpdated + " rows.");
  return totalUpdated;
}

function syncRowToTurso(sheet, rowNum, isBatch = false) {
  const displayTime = sheet.getRange(rowNum, 1).getDisplayValue(); 
  const data = sheet.getRange(rowNum, 1, 1, 10).getValues()[0];
  
  const entry = {
    time: displayTime,
    coachName: String(data[1]).trim(),
    groupName: String(data[2]).trim(),
    kidName: String(data[3]).trim(),
    parentEmail: String(data[8]).trim()
  };

  if (!entry.groupName || entry.groupName === "" || entry.groupName === "Group") {
    if (!entry.kidName) return;
  }

  const sheetName = sheet.getName();
  const dayOfWeek = getDayFromSheet(sheetName);
  const fullDay = getFullDayName(dayOfWeek);
  const displaySchedule = fullDay + " " + entry.time;

  // 1. Ensure Family User exists
  const sqlUser = {
    query: "INSERT INTO users (email, full_name, role, password) SELECT ?, ?, 'family', 'temp_pass' WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = ?)",
    args: [entry.parentEmail, entry.kidName + " Family", entry.parentEmail]
  };

  // 2. Fetch coach_id
  const coachResult = executeBatch([{
    query: "SELECT id FROM users WHERE full_name = ? AND role = 'coach' LIMIT 1",
    args: [entry.coachName]
  }]);
  
  let coachId = null;
  if (coachResult.status === "success" && coachResult.data.results[0].response.result.rows.length > 0) {
    coachId = coachResult.data.results[0].response.result.rows[0][0].value;
  }

  // 3. Upsert Group (Distinguished by name AND coach_id)
  const sqlGroup = {
    query: `INSERT INTO groups (name, schedule, coach_id) 
            VALUES (?, ?, ?) 
            ON CONFLICT(name, coach_id) DO UPDATE SET 
            schedule = excluded.schedule`,
    args: [entry.groupName, displaySchedule, coachId]
  };

  // 4. Enroll Student
  const sqlEnroll = {
    query: `INSERT INTO group_members (group_id, family_id, kid_name) 
            SELECT g.id, u.id, ? 
            FROM groups g, users u 
            WHERE g.name = ? AND (g.coach_id = ? OR (g.coach_id IS NULL AND ? IS NULL)) 
            AND u.email = ? 
            ON CONFLICT DO NOTHING`,
    args: [entry.kidName, entry.groupName, coachId, coachId, entry.parentEmail]
  };

  // 5. Update Schedule
  const batch = [sqlUser, sqlGroup, sqlEnroll];

  if (!isBatch) {
    // If not a full sync, we clear sessions for this specific time/group to update them
    // This is still imperfect for onEdit but safer than wiping the whole day
    batch.push({
      query: "DELETE FROM group_schedules WHERE group_id IN (SELECT id FROM groups WHERE name = ? AND (coach_id = ? OR (coach_id IS NULL AND ? IS NULL))) AND day_of_week = ? AND start_time = ?",
      args: [entry.groupName, coachId, coachId, dayOfWeek, entry.time]
    });
  }

  batch.push({
    query: `INSERT INTO group_schedules (group_id, day_of_week, start_time, end_time, court) 
            SELECT id, ?, ?, ?, 'Court 1' 
            FROM groups 
            WHERE name = ? AND (coach_id = ? OR (coach_id IS NULL AND ? IS NULL))`,
    args: [dayOfWeek, entry.time, entry.time, entry.groupName, coachId, coachId]
  });

  return executeBatch(batch);
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
    const content = response.getContentText();
    
    if (code !== 200) {
      Logger.log("ERROR: Turso API error (" + code + "): " + content);
      return { status: "error", code: code, message: content };
    }

    const data = JSON.parse(content);
    if (data.results) {
      data.results.forEach((res, idx) => {
        if (res.type === "error") {
          Logger.log("ERROR in statement " + idx + " (" + statements[idx].query + "): " + res.error.message);
        }
      });
    }
    return { status: "success", data: data };
  } catch (e) {
    Logger.log("ERROR: Fetch failed: " + e.toString());
    return { status: "error", message: e.toString() };
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
    } else if (payload.action === "sync_all") {
       const count = syncAllData();
       return createJsonResponse({ status: "success", message: "Full sync triggered", rows_processed: count });
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
  
  sheets.forEach(sheet => {
    const sheetName = sheet.getName().toLowerCase();
    if (Object.keys(DAYS_MAP).some(day => sheetName.includes(day)) || sheetName.includes("data")) {
      const data = sheet.getDataRange().getValues();
      
      for (let i = 1; i < data.length; i++) { // Skip header
        const rowKidName = String(data[i][3]).trim();
        const rowEmail = String(data[i][8]).trim();
        const rowGroupName = String(data[i][2]).trim();
        
        let match = false;
        if (originalKidName.toLowerCase() === rowKidName.toLowerCase()) {
          if (parentEmail && rowEmail.toLowerCase() === parentEmail.toLowerCase()) match = true;
          else if (originalGroupName && rowGroupName.toLowerCase() === originalGroupName.toLowerCase()) match = true;
          else if (!parentEmail && !originalGroupName) match = true;
        }

        if (match) {
           if (newKidName) sheet.getRange(i + 1, 4).setValue(newKidName);
           if (newParentEmail) sheet.getRange(i + 1, 9).setValue(newParentEmail);
           if (newGroupName) sheet.getRange(i + 1, 3).setValue(newGroupName);
           
           SpreadsheetApp.flush();
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
  const { originalGroupName, originalCoachName, newGroupName, newCoachName, newScheduleTime, dayOfWeek } = payload;
  
  if (!originalGroupName) {
    return createJsonResponse({ status: "error", message: "originalGroupName is required" }, 400);
  }

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let updatedRows = 0;
  
  // Helper to check if a row matches the original group + optional coach
  const isMatch = (dataRow) => {
    const rowGroupName = String(dataRow[2]).trim().toLowerCase();
    const rowCoachName = String(dataRow[1]).trim().toLowerCase();
    
    if (rowGroupName !== originalGroupName.toLowerCase()) return false;
    
    // If originalCoachName is provided, it must match
    if (originalCoachName && rowCoachName !== originalCoachName.toLowerCase()) return false;
    
    return true;
  };

  const sheets = ss.getSheets();
  sheets.forEach(sheet => {
    const sheetName = sheet.getName().toLowerCase();
    // Use dayOfWeek filter if provided, otherwise check all relevant sheets
    if (dayOfWeek && !sheetName.includes(dayOfWeek.toLowerCase())) return;
    
    if (Object.keys(DAYS_MAP).some(day => sheetName.includes(day)) || sheetName.includes("data")) {
      const data = sheet.getDataRange().getValues();
      for (let i = 1; i < data.length; i++) {
         if (isMatch(data[i])) {
             if (newGroupName) sheet.getRange(i + 1, 3).setValue(newGroupName);
             if (newCoachName) sheet.getRange(i + 1, 2).setValue(newCoachName);
             if (newScheduleTime) sheet.getRange(i + 1, 1).setValue(newScheduleTime);
             
             SpreadsheetApp.flush();
             syncRowToTurso(sheet, i + 1);
             updatedRows++;
         }
      }
    }
  });

  if (updatedRows > 0) {
    return createJsonResponse({ status: "success", message: `Updated and synced ${updatedRows} rows` });
  } else {
    return createJsonResponse({ status: "not_found", message: "Group not found in spreadsheet" }, 404);
  }
}

