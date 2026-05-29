# Optional Google Apps Script Setup Guide

The portal can create the Google Sheet tabs automatically, but this script gives you a quick manual headstart.

File included:

```text
google_apps_script/setup_portal_sheets_and_drive.gs
```

## What the script does

- Creates these Google Sheet tabs:
  - Users
  - Progress
  - StudentNotes
  - DayNotes
  - DayFiles
  - DayButtons
- Adds the correct header row.
- Seeds default Day 1 to Day 14 download buttons.
- Creates one Google Drive folder named `BST Internship Portal Files`.
- Logs the Sheet ID and Drive Folder ID.

## How to run

1. Open the Google Sheet you want to use.
2. Go to **Extensions > Apps Script**.
3. Paste the script.
4. Click **Run**.
5. Allow Google permission.
6. Go to **View > Logs**.
7. Copy:
   - Google Sheet ID
   - Drive Folder ID

## Important

After the Drive folder is created, share the Drive folder with your Service Account email as **Editor**.

The service account email looks like:

```text
something@project-id.iam.gserviceaccount.com
```

Then add this in Vercel:

```text
GOOGLE_DRIVE_FOLDER_ID=your_folder_id
```
