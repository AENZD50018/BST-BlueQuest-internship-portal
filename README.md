# BST Internship BlueQuest Portal - Google Sheets + Vercel Version V4

This version is designed for a free/simple setup:

- Vercel hosts the Flask portal.
- Google Sheets stores accounts, progress, notes, button labels and file links.
- Google Drive stores PDF/DOCX/ZIP files.

## New in V4

- Admin can edit the **button text** shown to students.
- Admin can edit the **button URL**.
- Admin can add/hide/delete buttons per day.
- Admin can edit extra file link text and URL.
- Admin can optionally upload files directly to Google Drive.
- Google Sheet tab names can be changed using environment variables.
- Added `DayButtons` sheet for the three top download buttons.

## Admin login

```text
Email: admin@bst.local
Password: admin123
```

You can change this with:

```text
ADMIN_EMAIL
ADMIN_PASSWORD
```

## Required Vercel Environment Variables

```text
SECRET_KEY
GOOGLE_SHEET_ID
GOOGLE_SERVICE_ACCOUNT_JSON
```

## Optional Environment Variables

```text
SHEET_USERS=Users
SHEET_PROGRESS=Progress
SHEET_STUDENT_NOTES=StudentNotes
SHEET_DAY_NOTES=DayNotes
SHEET_DAY_FILES=DayFiles
SHEET_DAY_BUTTONS=DayButtons
FULL_PROJECT_ZIP_URL=https://drive.google.com/your-project-zip
GOOGLE_DRIVE_FOLDER_ID=your_google_drive_folder_id
ADMIN_EMAIL=admin@bst.local
ADMIN_PASSWORD=admin123
```

## How to edit the buttons students see

1. Login as admin.
2. Open `/admin`.
3. Click any day.
4. Go to **Edit Download Buttons**.
5. Change text such as:

```text
Download Updated Day 2 Notes
Download Original Day Notes
Download Full Project ZIP
```

6. Change URL, order, style and visibility.
7. Click **Update Button**.

## Internal button URLs

Updated notes download:

```text
/download/day/2/notes
```

Original notes download:

```text
/download/day/2/original
```

External files:

```text
https://drive.google.com/file/d/....
```

## Google Drive method

Simple method:

1. Upload your notes/project files manually to Google Drive.
2. Share as Anyone with link can view.
3. Copy the link.
4. Add it in Admin > Manage Day > Add Google Drive / Docs File Link.

Optional direct upload:

1. Create a Google Drive folder.
2. Share it with the service account email as Editor.
3. Add its folder ID as `GOOGLE_DRIVE_FOLDER_ID`.
4. Use Admin > Manage Day > Upload File to Google Drive.

## Local run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000/setup
```

## Vercel

The included `vercel.json` routes all requests to `app.py`.

Vercel build command:

```text
pip install -r requirements.txt
```

Vercel will use the Python runtime automatically.
