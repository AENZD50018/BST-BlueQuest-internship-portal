# Google Sheet Structure - V4 Editable Version

The app creates these tabs automatically when you open `/setup` or when the first request runs.

You can rename the tabs using Vercel/local environment variables.

## Default Sheet Tab Names

| Purpose | Default Tab Name | Environment Variable |
|---|---|---|
| Login accounts | Users | SHEET_USERS |
| Day completion ticks | Progress | SHEET_PROGRESS |
| Student daily notes | StudentNotes | SHEET_STUDENT_NOTES |
| Admin day notes | DayNotes | SHEET_DAY_NOTES |
| Extra Google Drive/file links | DayFiles | SHEET_DAY_FILES |
| Student download buttons | DayButtons | SHEET_DAY_BUTTONS |

## Headers

### Users

```text
id, email, password_hash, name, role, avatar, created_at, last_login
```

### Progress

```text
user_id, day, completed, updated_at
```

### StudentNotes

```text
user_id, day, note, updated_at
```

### DayNotes

```text
day, title, description, content, updated_at
```

### DayFiles

```text
id, day, title, url, updated_at
```

### DayButtons

```text
id, day, button_text, url, style, sort_order, is_visible, updated_at
```

## DayButtons explanation

These control the buttons students see under **Files and Notes**.

Example rows:

```text
day02-updated-notes, 2, Download Updated Day 2 Notes, /download/day/2/notes, btn, 10, TRUE, ...
day02-original-notes, 2, Download Original Day Notes, /download/day/2/original, ghost, 20, TRUE, ...
day02-project-zip, 2, Download Full Project ZIP, https://drive.google.com/..., ghost, 30, TRUE, ...
```

### style values

```text
btn   = blue main button
ghost = dark outline button
```

### is_visible values

```text
TRUE  = show to students
FALSE = hide from students
```

## Google Drive use

Recommended simple method:

1. Create a Google Drive folder.
2. Upload PDFs/DOCX/ZIP files manually.
3. Right click file > Share > Anyone with link can view.
4. Copy the public URL.
5. Admin portal > Manage Day > Add Google Drive / Docs File Link.

Optional direct upload method:

1. Create a Google Drive folder.
2. Share the folder with the service account email as Editor.
3. Put the folder ID in `GOOGLE_DRIVE_FOLDER_ID`.
4. Admin can use “Upload File to Google Drive” from the portal.

Folder ID example:

```text
https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOp
Folder ID = 1AbCdEfGhIjKlMnOp
```
