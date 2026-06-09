// SF TENNIS KIDS - AUTO-SYNC v7 (onEdit + Hourly Trigger + Webhook)
/*
   ==========================================================================
   DEPLOYMENT INSTRUCTIONS:
   1. Open your Google Sheet.
   2. Go to Extensions > Apps Script.
   3. DELETE ALL existing code.
   4. PASTE THIS ENTIRE FILE.
   5. Update CONFIG.webhookUrl and CONFIG.syncKey below.
   6. Click Deploy > New Deployment.
   7. Execute as: Me | Access: Anyone.
   8. In the editor, run installHourlyTrigger() once.
   9. The onEdit trigger activates automatically (simple trigger).
   ==========================================================================
*/

var CONFIG = {
  webhookUrl: "https://tennis-academy-six.vercel.app",
  syncKey: "7C3A8E1F-2B4D-4F6E-9A0B-1C2D3E4F5G6H",
  debounceMs: 30000,
};

// ---- Turso config (from v6) ----
var TURSO_URL = "https://sfchat-gelenmp.aws-eu-west-1.turso.io";
var TURSO_TOKEN =
  "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzIxMjExMDMsImlkIjoi" +
  "MDE5Yzk5ZGQtZjAwMS03ZTgyLWFjMDMtZmIwMDg5ZTdhN2ZlIiwicmlkIjoi" +
  "OTg4YzJhN2UtZDI3ZS00NmQ5LWE4OTQtYTBhYTIxYzliMzFmIn0." +
  "wo6KD364yHQu5wYq-XSudYjxagJQCV2vmWNdx0Q2DBPGm_euPJl6blkU-fS453_NEdO5dZUz--HsjBlJth0BBQ";

var DAYS_MAP = {
  monday: 0, mon: 0, tuesday: 1, tue: 1, wednesday: 2, wed: 2,
  thursday: 3, thu: 3, friday: 4, fri: 4, saturday: 5, sat: 5, sunday: 6, sun: 6,
};

var lastSyncTime = 0;

// ---- Installable Triggers (must be installed via install* functions) ----

/**
 * onSheetEdit — fires on any cell edit (installable trigger).
 * Debounces to avoid flooding on rapid typing.
 * NOTE: Must be installed via installOnEditTrigger() — simple onEdit() can't do HTTP.
 */
function onSheetEdit(e) {
  var now = Date.now();
  if (now - lastSyncTime < CONFIG.debounceMs) return;
  lastSyncTime = now;

  var range = e.range;
  var sheetName = range.getSheet().getName().toUpperCase();
  var row = range.getRow();
  if (row < 2) return; // skip header row

  Logger.log("onSheetEdit: sheet=" + sheetName + " row=" + row);

  try {
    var result = syncAllData();
    notifyFlask("sync_all", result.rows_processed || 0);
    Logger.log("onSheetEdit sync complete: " + JSON.stringify(result));
  } catch (error) {
    Logger.log("onSheetEdit sync error: " + error.toString());
  }
}

// ---- Timed Triggers ----

/**
 * syncAll — called by hourly time-based trigger.
 */
function syncAll() {
  Logger.log("Hourly sync starting...");
  try {
    var result = syncAllData();
    notifyFlask("sync_all", result.rows_processed || 0);
    Logger.log("Hourly sync complete: " + JSON.stringify(result));
  } catch (error) {
    Logger.log("Hourly sync error: " + error.toString());
  }
}

/**
 * Install the onEdit installable trigger.
 * Run this ONCE from the editor after deploying.
 * This is REQUIRED for the auto-sync to work (simple onEdit can't do HTTP).
 */
function installOnEditTrigger() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function (t) {
    if (t.getHandlerFunction() === "onSheetEdit") {
      ScriptApp.deleteTrigger(t);
    }
  });

  ScriptApp.newTrigger("onSheetEdit")
    .forSpreadsheet(ss)
    .onEdit()
    .create();

  Logger.log("onEdit trigger installed for: " + ss.getName());
}

/**
 * Install the hourly time-based trigger.
 * Run this ONCE from the editor after deploying.
 */
function installHourlyTrigger() {
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function (t) {
    if (t.getHandlerFunction() === "syncAll") {
      ScriptApp.deleteTrigger(t);
    }
  });

  ScriptApp.newTrigger("syncAll")
    .timeBased()
    .everyHours(1)
    .create();

  Logger.log("Hourly trigger installed.");
}

// ---- Webhook Notification to Flask ----

function notifyFlask(action, rowsProcessed) {
  var payload = {
    action: action,
    rows_processed: rowsProcessed,
    source: action === "sync_all" ? "timer" : "onEdit",
  };

  var options = {
    method: "post",
    headers: {
      "X-Sync-Key": CONFIG.syncKey,
      "Content-Type": "application/json",
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  };

  try {
    var response = UrlFetchApp.fetch(
      CONFIG.webhookUrl + "/api/webhook/sheets-sync",
      options
    );
    Logger.log("Flask notified: " + response.getContentText());
  } catch (error) {
    Logger.log("Failed to notify Flask: " + error.toString());
  }
}

// ---- Existing v6 Sync Logic (unchanged) ----

function doPost(e) {
  try {
    var payload = JSON.parse(e.postData.contents);
    if (payload.action === "sync_all") {
      return createJsonResponse(syncAllData());
    }
    return createJsonResponse({ status: "success", info: "Action received" });
  } catch (error) {
    return createJsonResponse({ status: "error", message: error.toString() }, 400);
  }
}

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
  val = val.toString().toLowerCase().replace(/\s+/g, "");
  val = val.replace(/\./g, "");
  if (val === "0" || val === "12:00am" || val === "12am") return "";
  return val;
}

function getPreferredCoachId(coachName) {
  if (!coachName || coachName.toString().trim() === "") return null;
  coachName = coachName.toString().trim();

  var coaches = tursoQuery("SELECT id, full_name FROM users WHERE role = 'coach'");
  var rows = coaches.results[0].response.result.rows;

  // First try exact match
  for (var i = 0; i < rows.length; i++) {
    var name = rows[i][1].value.toLowerCase().trim();
    if (name === coachName.toLowerCase().trim()) {
      return parseInt(rows[i][0].value);
    }
  }

  // Then try contains match
  for (var j = 0; j < rows.length; j++) {
    var coach = rows[j][1].value.toLowerCase().trim();
    if (coach.includes(coachName.toLowerCase()) || coachName.toLowerCase().includes(coach)) {
      return parseInt(rows[j][0].value);
    }
  }

  return null;
}

function syncAllData() {
  var sheetNames = [
    "MONDAY",
    "TUESDAY",
    "WEDNESDAYS",
    "THURSDAY",
    "FRIDAY",
    "SATURDAY",
    "SUNDAY",
  ];
  var totalEnrollments = 0;
  var totalSessions = 0;
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  // Phase 1: Clear existing group_schedules and group_members
  tursoQuery("DELETE FROM group_schedules");
  tursoQuery("DELETE FROM group_members");

  for (var s = 0; s < sheetNames.length; s++) {
    var sheetName = sheetNames[s];
    var sheet = ss.getSheetByName(sheetName);
    if (!sheet) continue;

    var data = sheet.getDataRange().getDisplayValues();
    if (data.length < 2) continue;

    // Map columns by header
    var headers = data[0];
    var colMap = {};
    for (var c = 0; c < headers.length; c++) {
      var h = headers[c].toString().toLowerCase().replace(/\s+/g, "");
      if (h.includes("time") || h.includes("hora")) colMap.time = c;
      else if (h.includes("coach") || h.includes("entrenador")) colMap.coach = c;
      else if (h.includes("group") || h.includes("grupo")) colMap.group = c;
      else if (h.includes("kid") || h.includes("niño") || h.includes("alumno")) colMap.kid = c;
      else if (h.includes("parent") && (h.includes("email") || h.includes("mail"))) colMap.parentEmail = c;
      else if (h.includes("parent") && (h.includes("name") || h.includes("nombre"))) colMap.parentName = c;
      else if (h.includes("phone") || h.includes("teléfono") || h.includes("celular")) colMap.phone = c;
    }

    var dayIndex = DAYS_MAP[sheetName.toLowerCase()] || 0;

    for (var r = 1; r < data.length; r++) {
      var row = data[r];
      var timeVal = colMap.time !== undefined ? cleanTime(row[colMap.time]) : "";
      var coachName = colMap.coach !== undefined ? row[colMap.coach].toString().trim() : "";
      var groupName = colMap.group !== undefined ? row[colMap.group].toString().trim() : "";
      var kidName = colMap.kid !== undefined ? row[colMap.kid].toString().trim() : "";

      if (!groupName || !kidName || !timeVal) continue;

      var endTime = calcEndTime(timeVal);
      var coachId = getPreferredCoachId(coachName);

      // Upsert group
      var existingGroup = tursoQuery(
        "SELECT id FROM groups WHERE name = ? AND coach_id = ?",
        [{ type: "text", value: groupName }, { type: "integer", value: coachId ? String(coachId) : "0" }]
      );
      var groupRows = existingGroup.results[0].response.result.rows;
      var groupId;

      if (groupRows.length > 0) {
        groupId = parseInt(groupRows[0][0].value);
      } else {
        var insertGroup = tursoQuery(
          "INSERT INTO groups (name, schedule, coach_id) VALUES (?, ?, ?)",
          [
            { type: "text", value: groupName },
            { type: "text", value: dayIndex + " " + timeVal },
            { type: "integer", value: coachId ? String(coachId) : "null" },
          ]
        );
        groupId = insertGroup.results[0].response.result.last_insert_rowid;
      }

      // Upsert group_schedule
      var schedResult = tursoQuery(
        "SELECT id FROM group_schedules WHERE group_id = ? AND day_of_week = ? AND start_time = ?",
        [
          { type: "integer", value: String(groupId) },
          { type: "integer", value: String(dayIndex) },
          { type: "text", value: timeVal },
        ]
      );
      var schedRows = schedResult.results[0].response.result.rows;
      var scheduleId;

      if (schedRows.length > 0) {
        scheduleId = parseInt(schedRows[0][0].value);
      } else {
        var insertSched = tursoQuery(
          "INSERT INTO group_schedules (group_id, day_of_week, start_time, end_time, court) VALUES (?, ?, ?, ?, 'Court 1')",
          [
            { type: "integer", value: String(groupId) },
            { type: "integer", value: String(dayIndex) },
            { type: "text", value: timeVal },
            { type: "text", value: endTime },
          ]
        );
        scheduleId = insertSched.results[0].response.result.last_insert_rowid;
      }

      totalSessions++;

      // Upsert group_member
      var parentEmail = colMap.parentEmail !== undefined ? row[colMap.parentEmail].toString().trim() : "";
      var parentName = colMap.parentName !== undefined ? row[colMap.parentName].toString().trim() : "";
      var phone = colMap.phone !== undefined ? row[colMap.phone].toString().trim() : "";

      var familyResult = tursoQuery(
        "SELECT id FROM users WHERE email = ? AND role = 'family'",
        [{ type: "text", value: parentEmail || "unknown@email.com" }]
      );
      var familyRows = familyResult.results[0].response.result.rows;
      var familyId;

      if (familyRows.length > 0) {
        familyId = parseInt(familyRows[0][0].value);
      } else {
        var insertFamily = tursoQuery(
          "INSERT INTO users (email, password, full_name, role, phone) VALUES (?, ?, ?, 'family', ?)",
          [
            { type: "text", value: parentEmail || "unknown@email.com" },
            { type: "text", value: "admin123" },
            { type: "text", value: parentName || kidName + "'s Parent" },
            { type: "text", value: phone || "" },
          ]
        );
        familyId = insertFamily.results[0].response.result.last_insert_rowid;
      }

      var enrollResult = tursoQuery(
        "SELECT id FROM group_members WHERE group_id = ? AND family_id = ? AND kid_name = ?",
        [
          { type: "integer", value: String(groupId) },
          { type: "integer", value: String(familyId) },
          { type: "text", value: kidName },
        ]
      );
      if (enrollResult.results[0].response.result.rows.length === 0) {
        tursoQuery(
          "INSERT INTO group_members (group_id, family_id, kid_name, schedule_id) VALUES (?, ?, ?, ?)",
          [
            { type: "integer", value: String(groupId) },
            { type: "integer", value: String(familyId) },
            { type: "text", value: kidName },
            { type: "integer", value: String(scheduleId) },
          ]
        );
        totalEnrollments++;
      }
    }
  }

  return {
    status: "success",
    rows_processed: totalEnrollments,
    version: "V7-AUTO-SYNC",
    sessions: totalSessions,
    enrollments: totalEnrollments,
  };
}

function calcEndTime(startTime) {
  startTime = startTime.toLowerCase().replace(/\s+/g, "");
  var match = startTime.match(/^(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$/);
  if (!match) return "";

  var hour = parseInt(match[1]);
  var min = match[2] ? parseInt(match[2]) : 0;
  var meridian = match[3] || "";
  var isPM = meridian === "pm";

  if (isPM && hour !== 12) hour += 12;
  if (!isPM && hour === 12) hour = 0;

  var totalMinutes = hour * 60 + min + 60; // +1 hour
  var endHour = Math.floor(totalMinutes / 60);
  var endMin = totalMinutes % 60;

  if (endHour >= 12) {
    var displayHour = endHour > 12 ? endHour - 12 : endHour;
    return displayHour + ":" + (endMin < 10 ? "0" : "") + endMin + "pm";
  }
  return endHour + ":" + (endMin < 10 ? "0" : "") + endMin + "am";
}

function tursoQuery(sql, params) {
  params = params || [];
  var pipeline = {
    requests: [{ type: "execute", stmt: { sql: sql, args: params } }],
  };

  var options = {
    method: "post",
    headers: {
      Authorization: "Bearer " + TURSO_TOKEN,
      "Content-Type": "application/json",
    },
    payload: JSON.stringify(pipeline),
    muteHttpExceptions: true,
  };

  var response = UrlFetchApp.fetch(TURSO_URL + "/v2/pipeline", options);
  return JSON.parse(response);
}

function createJsonResponse(data, statusCode) {
  statusCode = statusCode || 200;
  return ContentService.createTextOutput(JSON.stringify(data)).setMimeType(
    ContentService.MimeType.JSON
  );
}
