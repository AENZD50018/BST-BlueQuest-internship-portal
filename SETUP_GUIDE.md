# Setup Guide - BST Internship BlueQuest V4

## 1. Create Google Cloud Service Account

1. Go to Google Cloud Console.
2. Create/select project.
3. Enable:
   - Google Sheets API
   - Google Drive API
4. Create a Service Account.
5. Create a JSON key and download it.
6. Copy the service account email.

## 2. Create Google Sheet

1. Create a blank Google Sheet.
2. Copy the Sheet ID from the URL.
3. Share the Sheet with the service account email as **Editor**.

## 3. Optional Google Drive folder

For file upload from admin portal:

1. Create a Google Drive folder.
2. Share the folder with the service account email as **Editor**.
3. Copy the folder ID.
4. Add it as `GOOGLE_DRIVE_FOLDER_ID`.

You can skip this and manually paste Google Drive file links instead.

## 4. Vercel Environment Variables

Required:

```text
SECRET_KEY
GOOGLE_SHEET_ID
GOOGLE_SERVICE_ACCOUNT_JSON
```

Optional:

```text
SHEET_USERS=Users
SHEET_PROGRESS=Progress
SHEET_STUDENT_NOTES=StudentNotes
SHEET_DAY_NOTES=DayNotes
SHEET_DAY_FILES=DayFiles
SHEET_DAY_BUTTONS=DayButtons
FULL_PROJECT_ZIP_URL=https://drive.google.com/your-project-zip
GOOGLE_DRIVE_FOLDER_ID=your_drive_folder_id
ADMIN_EMAIL=admin@bst.local
ADMIN_PASSWORD=admin123
```

## 5. First run

Open:

```text
https://your-site.vercel.app/setup
```

This creates the sheets, default admin and default Day 1 to Day 14 buttons.

## 6. Editing student download buttons

Admin > Manage Day > Edit Download Buttons.

You can change:

- Button text
- Button URL
- Style
- Order
- Visibility

## 7. Default internal download URLs

Updated notes:

```text
/download/day/1/notes
```

Original notes:

```text
/download/day/1/original
```

Use Google Drive links for PDFs, DOCX and ZIP files.
