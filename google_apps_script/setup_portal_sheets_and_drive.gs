/**
 * BST Internship BlueQuest Portal - Google Sheets Setup Helper
 *
 * How to use:
 * 1. Open your Google Sheet.
 * 2. Extensions > Apps Script.
 * 3. Paste this file.
 * 4. Click Run > setupPortalSheetsAndDrive.
 * 5. Check Logs for the created Drive folder ID.
 *
 * This script is optional. The Flask app can also create the tabs automatically.
 */

const SHEET_NAMES = {
  USERS: 'Users',
  PROGRESS: 'Progress',
  STUDENT_NOTES: 'StudentNotes',
  DAY_NOTES: 'DayNotes',
  DAY_FILES: 'DayFiles',
  DAY_BUTTONS: 'DayButtons'
};

const HEADERS = {
  Users: ['id', 'email', 'password_hash', 'name', 'role', 'avatar', 'created_at', 'last_login'],
  Progress: ['user_id', 'day', 'completed', 'updated_at'],
  StudentNotes: ['user_id', 'day', 'note', 'updated_at'],
  DayNotes: ['day', 'title', 'description', 'content', 'updated_at'],
  DayFiles: ['id', 'day', 'title', 'url', 'updated_at'],
  DayButtons: ['id', 'day', 'button_text', 'url', 'style', 'sort_order', 'is_visible', 'updated_at']
};

function setupPortalSheetsAndDrive() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  Object.keys(SHEET_NAMES).forEach(function(key) {
    const tabName = SHEET_NAMES[key];
    let sheet = ss.getSheetByName(tabName);
    if (!sheet) {
      sheet = ss.insertSheet(tabName);
    }

    const headers = HEADERS[tabName];
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    sheet.setFrozenRows(1);
    sheet.autoResizeColumns(1, headers.length);
  });

  seedDayButtons(ss);

  const folder = DriveApp.createFolder('BST Internship Portal Files');
  Logger.log('Google Sheet ID: ' + ss.getId());
  Logger.log('Drive Folder ID: ' + folder.getId());
  Logger.log('Share this folder with the service account email as Editor.');
}

function seedDayButtons(ss) {
  const sheet = ss.getSheetByName(SHEET_NAMES.DAY_BUTTONS);
  const existingValues = sheet.getDataRange().getValues();
  const existingIds = existingValues.slice(1).map(row => String(row[0]));
  const rows = [];
  const now = new Date();

  for (let day = 1; day <= 14; day++) {
    const dayText = String(day).padStart(2, '0');
    const defaults = [
      [`day${dayText}-updated-notes`, day, `Download Updated Day ${day} Notes`, `/download/day/${day}/notes`, 'btn', 10, 'TRUE', now],
      [`day${dayText}-original-notes`, day, 'Download Original Day Notes', `/download/day/${day}/original`, 'ghost', 20, 'TRUE', now],
      [`day${dayText}-project-zip`, day, 'Download Full Project ZIP', '#', 'ghost', 30, 'TRUE', now]
    ];

    defaults.forEach(row => {
      if (!existingIds.includes(row[0])) {
        rows.push(row);
      }
    });
  }

  if (rows.length > 0) {
    sheet.getRange(sheet.getLastRow() + 1, 1, rows.length, rows[0].length).setValues(rows);
  }
}
