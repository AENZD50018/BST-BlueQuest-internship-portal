
import os
import json
import base64
import uuid
import io
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import gspread
from google.oauth2.service_account import Credentials
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from days import DAYS, get_day

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
except Exception:  # keeps local setup friendly until package is installed
    build = None
    MediaIoBaseUpload = None

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ------------------------------------------------------------
# CHANGE SHEET NAMES HERE OR IN VERCEL ENVIRONMENT VARIABLES
# ------------------------------------------------------------
# Example Vercel env variable:
# SHEET_USERS=Students_Login
# SHEET_DAY_BUTTONS=Daily_Buttons
SHEET_USERS = os.environ.get("SHEET_USERS", "Users")
SHEET_PROGRESS = os.environ.get("SHEET_PROGRESS", "Progress")
SHEET_STUDENT_NOTES = os.environ.get("SHEET_STUDENT_NOTES", "StudentNotes")
SHEET_DAY_NOTES = os.environ.get("SHEET_DAY_NOTES", "DayNotes")
SHEET_DAY_FILES = os.environ.get("SHEET_DAY_FILES", "DayFiles")
SHEET_DAY_BUTTONS = os.environ.get("SHEET_DAY_BUTTONS", "DayButtons")
SHEET_DAY_SETTINGS = os.environ.get("SHEET_DAY_SETTINGS", "DaySettings")
SHEET_SUBMISSIONS = os.environ.get("SHEET_SUBMISSIONS", "Submissions")

SHEET_HEADERS = {
    SHEET_USERS: ["id", "email", "password_hash", "name", "role", "avatar", "created_at", "last_login"],
    SHEET_PROGRESS: ["user_id", "day", "completed", "updated_at"],
    SHEET_STUDENT_NOTES: ["user_id", "day", "note", "updated_at"],
    SHEET_DAY_NOTES: ["day", "title", "description", "content", "updated_at"],
    SHEET_DAY_FILES: ["id", "day", "title", "url", "updated_at"],
    SHEET_DAY_BUTTONS: ["id", "day", "button_text", "url", "style", "sort_order", "is_visible", "updated_at"],
    SHEET_DAY_SETTINGS: ["day", "submission_required", "submission_title", "submission_help", "updated_at"],
    SHEET_SUBMISSIONS: ["id", "user_id", "day", "submission_text", "submission_url", "status", "submitted_at", "updated_at"],
}

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@bst.local")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
DEFAULT_PROJECT_ZIP_URL = os.environ.get("FULL_PROJECT_ZIP_URL", "#")
GOOGLE_DRIVE_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "").strip()


class ConfigError(Exception):
    pass


_cache = {}
_spreadsheet = None
_drive_service = None


def now_text() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def _parse_service_account_info() -> dict:
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        raise ConfigError(
            "GOOGLE_SERVICE_ACCOUNT_JSON environment variable is missing.")

    try:
        if raw.startswith("{"):
            return json.loads(raw)
        decoded = base64.b64decode(raw).decode("utf-8")
        return json.loads(decoded)
    except Exception as exc:
        raise ConfigError(
            "GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON or base64 JSON.") from exc


def get_service_account_email() -> str:
    try:
        info = _parse_service_account_info()
        return info.get("client_email", "")
    except Exception:
        return ""


def get_sheet_config_for_admin() -> dict:
    return {
        "GOOGLE_SHEET_ID": os.environ.get("GOOGLE_SHEET_ID", ""),
        "GOOGLE_DRIVE_FOLDER_ID": GOOGLE_DRIVE_FOLDER_ID,
        "SHEET_USERS": SHEET_USERS,
        "SHEET_PROGRESS": SHEET_PROGRESS,
        "SHEET_STUDENT_NOTES": SHEET_STUDENT_NOTES,
        "SHEET_DAY_NOTES": SHEET_DAY_NOTES,
        "SHEET_DAY_FILES": SHEET_DAY_FILES,
        "SHEET_DAY_BUTTONS": SHEET_DAY_BUTTONS,
        "service_account_email": get_service_account_email(),
    }


def get_spreadsheet():
    global _spreadsheet
    if _spreadsheet is not None:
        return _spreadsheet

    sheet_id = os.environ.get("GOOGLE_SHEET_ID", "").strip()
    if not sheet_id:
        raise ConfigError("GOOGLE_SHEET_ID environment variable is missing.")

    info = _parse_service_account_info()
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    client = gspread.authorize(creds)

    try:
        _spreadsheet = client.open_by_key(sheet_id)
    except Exception as exc:
        raise ConfigError(
            "Could not open Google Sheet. Check GOOGLE_SHEET_ID and share the sheet with the service account email as Editor."
        ) from exc

    return _spreadsheet


def get_drive_service():
    global _drive_service
    if _drive_service is not None:
        return _drive_service
    if build is None or MediaIoBaseUpload is None:
        raise ConfigError(
            "google-api-python-client is not installed. Run: pip install google-api-python-client")
    info = _parse_service_account_info()
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    _drive_service = build("drive", "v3", credentials=creds)
    return _drive_service


def worksheet(title: str):
    ss = get_spreadsheet()
    try:
        return ss.worksheet(title)
    except gspread.WorksheetNotFound:
        return ss.add_worksheet(title=title, rows=500, cols=20)


def invalidate_cache():
    _cache.clear()


def get_records(sheet_name: str, ttl_seconds: int = 8) -> List[dict]:
    key = f"records:{sheet_name}"
    ts = datetime.utcnow().timestamp()
    if key in _cache:
        cached_ts, cached_value = _cache[key]
        if ts - cached_ts < ttl_seconds:
            return cached_value

    ws = worksheet(sheet_name)
    rows = ws.get_all_records()
    _cache[key] = (ts, rows)
    return rows


def ensure_headers():
    """Create/update sheet header rows without deleting existing data."""
    for sheet_name, headers in SHEET_HEADERS.items():
        ws = worksheet(sheet_name)
        existing = ws.row_values(1)
        if not existing:
            ws.append_row(headers)
        elif existing != headers:
            end_col = chr(ord('A') + len(headers) - 1)
            ws.update(f"A1:{end_col}1", [headers])


def row_number_by_value(sheet_name: str, column_name: str, value: str) -> Optional[int]:
    ws = worksheet(sheet_name)
    headers = ws.row_values(1)
    if column_name not in headers:
        return None
    col_no = headers.index(column_name) + 1
    col_values = ws.col_values(col_no)
    for index, cell in enumerate(col_values, start=1):
        if str(cell) == str(value):
            return index
    return None


def row_number_by_two_values(sheet_name: str, col1: str, val1: str, col2: str, val2: str) -> Optional[int]:
    ws = worksheet(sheet_name)
    headers = ws.row_values(1)
    if col1 not in headers or col2 not in headers:
        return None

    c1 = headers.index(col1)
    c2 = headers.index(col2)
    values = ws.get_all_values()

    for idx, row in enumerate(values[1:], start=2):
        row = row + [""] * (len(headers) - len(row))
        if str(row[c1]) == str(val1) and str(row[c2]) == str(val2):
            return idx
    return None


def seed_days():
    records = get_records(SHEET_DAY_NOTES, ttl_seconds=0)
    existing_days = {str(r.get("day")) for r in records}

    ws = worksheet(SHEET_DAY_NOTES)
    for day in DAYS:
        if str(day["day"]) not in existing_days:
            ws.append_row([
                str(day["day"]),
                day["title"],
                day["task"],
                day["default_notes"],
                now_text()
            ])
    invalidate_cache()


def default_button_rows(day_no: int) -> List[List[str]]:
    return [
        [
            f"day{day_no:02d}-updated-notes",
            str(day_no),
            f"Download Updated Day {day_no} Notes",
            f"/download/day/{day_no}/notes",
            "btn",
            "10",
            "TRUE",
            now_text(),
        ],
        [
            f"day{day_no:02d}-original-notes",
            str(day_no),
            "Download Original Day Notes",
            f"/download/day/{day_no}/original",
            "ghost",
            "20",
            "TRUE",
            now_text(),
        ],
        [
            f"day{day_no:02d}-project-zip",
            str(day_no),
            "Download Full Project ZIP",
            DEFAULT_PROJECT_ZIP_URL,
            "ghost",
            "30",
            "TRUE",
            now_text(),
        ],
    ]


def seed_day_buttons():
    records = get_records(SHEET_DAY_BUTTONS, ttl_seconds=0)
    existing_ids = {str(r.get("id")) for r in records}
    ws = worksheet(SHEET_DAY_BUTTONS)
    for day in DAYS:
        for row in default_button_rows(int(day["day"])):
            if row[0] not in existing_ids:
                ws.append_row(row)
    invalidate_cache()


def seed_admin():
    if not find_user_by_email(ADMIN_EMAIL):
        create_user(
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD,
            name="BST Admin",
            role="admin",
            avatar="🛡️"
        )


def initialize_sheet():
    ensure_headers()
    seed_days()
    seed_day_buttons()
    seed_admin()


def find_user_by_email(email: str) -> Optional[dict]:
    email = email.strip().lower()
    for user in get_records(SHEET_USERS):
        if str(user.get("email", "")).strip().lower() == email:
            return user
    return None


def find_user_by_id(user_id: str) -> Optional[dict]:
    for user in get_records(SHEET_USERS):
        if str(user.get("id", "")) == str(user_id):
            return user
    return None


def create_user(email: str, password: str, name: str, role: str = "student", avatar: str = "🧑‍💻") -> dict:
    email = email.strip().lower()
    if find_user_by_email(email):
        raise ValueError("Email already registered.")

    user_id = str(uuid.uuid4())[:12]
    ws = worksheet(SHEET_USERS)
    user = {
        "id": user_id,
        "email": email,
        "password_hash": generate_password_hash(password),
        "name": name.strip(),
        "role": role,
        "avatar": avatar,
        "created_at": now_text(),
        "last_login": ""
    }
    ws.append_row([user[h] for h in SHEET_HEADERS[SHEET_USERS]])
    invalidate_cache()
    return user


def authenticate(email: str, password: str) -> Optional[dict]:
    user = find_user_by_email(email)
    if not user:
        return None

    if check_password_hash(str(user.get("password_hash", "")), password):
        row_no = row_number_by_value(SHEET_USERS, "id", user["id"])
        if row_no:
            ws = worksheet(SHEET_USERS)
            headers = ws.row_values(1)
            last_login_col = headers.index("last_login") + 1
            ws.update_cell(row_no, last_login_col, now_text())
            invalidate_cache()
        return user
    return None


def get_progress(user_id: str) -> Dict[int, bool]:
    rows = get_records(SHEET_PROGRESS)
    progress = {}
    for row in rows:
        if str(row.get("user_id")) == str(user_id):
            try:
                progress[int(row.get("day"))] = str(
                    row.get("completed", "")).upper() == "TRUE"
            except Exception:
                pass
    return progress


def get_progress_stats(user_id: str) -> Tuple[Dict[int, bool], int, int, int, int, int]:
    progress = get_progress(user_id)
    total_days = len(DAYS)
    completed_days = len([day for day, done in progress.items() if done])
    percent = int((completed_days / total_days) * 100) if total_days else 0
    xp = completed_days * 10
    level = max(1, (xp // 30) + 1)
    return progress, completed_days, total_days, percent, xp, level


def set_progress(user_id: str, day: int, completed: bool):
    row_no = row_number_by_two_values(
        SHEET_PROGRESS, "user_id", str(user_id), "day", str(day))
    ws = worksheet(SHEET_PROGRESS)
    values = [str(user_id), str(day),
              "TRUE" if completed else "FALSE", now_text()]
    if row_no:
        ws.update(f"A{row_no}:D{row_no}", [values])
    else:
        ws.append_row(values)
    invalidate_cache()


def get_student_note(user_id: str, day: int) -> str:
    rows = get_records(SHEET_STUDENT_NOTES)
    for row in rows:
        if str(row.get("user_id")) == str(user_id) and str(row.get("day")) == str(day):
            return str(row.get("note", ""))
    return ""


def save_student_note(user_id: str, day: int, note: str):
    row_no = row_number_by_two_values(
        SHEET_STUDENT_NOTES, "user_id", str(user_id), "day", str(day))
    ws = worksheet(SHEET_STUDENT_NOTES)
    values = [str(user_id), str(day), note, now_text()]
    if row_no:
        ws.update(f"A{row_no}:D{row_no}", [values])
    else:
        ws.append_row(values)
    invalidate_cache()


def get_day_note(day: int) -> dict:
    default = get_day(day)
    rows = get_records(SHEET_DAY_NOTES)
    for row in rows:
        if str(row.get("day")) == str(day):
            return {
                "day": day,
                "title": str(row.get("title", "")) or default["title"],
                "description": str(row.get("description", "")) or default["task"],
                "content": str(row.get("content", "")) or default["default_notes"],
                "updated_at": str(row.get("updated_at", ""))
            }
    return {
        "day": day,
        "title": default["title"],
        "description": default["task"],
        "content": default["default_notes"],
        "updated_at": ""
    }


def update_day_note(day: int, title: str, description: str, content: str):
    row_no = row_number_by_value(SHEET_DAY_NOTES, "day", str(day))
    ws = worksheet(SHEET_DAY_NOTES)
    values = [str(day), title, description, content, now_text()]
    if row_no:
        ws.update(f"A{row_no}:E{row_no}", [values])
    else:
        ws.append_row(values)
    invalidate_cache()


def get_original_day_note(day: int) -> dict:
    default = get_day(day)
    return {
        "day": day,
        "title": default["title"],
        "description": default["task"],
        "content": default["default_notes"],
        "updated_at": "original"
    }


def _as_visible(value) -> bool:
    return str(value).strip().upper() not in {"FALSE", "NO", "0", "HIDE", ""}


def list_day_buttons(day: int) -> List[dict]:
    buttons = []
    for row in get_records(SHEET_DAY_BUTTONS):
        if str(row.get("day")) == str(day):
            button = dict(row)
            button["visible_bool"] = _as_visible(row.get("is_visible", "TRUE"))
            try:
                button["sort_number"] = int(row.get("sort_order") or 999)
            except Exception:
                button["sort_number"] = 999
            button["style"] = str(row.get("style", "ghost") or "ghost").lower()
            button["button_text"] = str(
                row.get("button_text", "Download") or "Download")
            button["url"] = str(row.get("url", "#") or "#")
            buttons.append(button)
    buttons.sort(key=lambda x: (x["sort_number"], x["button_text"]))
    return buttons


def add_day_button(day: int, button_text: str, url: str, style: str = "ghost", sort_order: str = "99", is_visible: bool = True):
    ws = worksheet(SHEET_DAY_BUTTONS)
    button_id = str(uuid.uuid4())[:12]
    ws.append_row([
        button_id,
        str(day),
        button_text.strip(),
        url.strip() or "#",
        style.strip() or "ghost",
        str(sort_order or "99"),
        "TRUE" if is_visible else "FALSE",
        now_text()
    ])
    invalidate_cache()


def update_day_button(button_id: str, button_text: str, url: str, style: str, sort_order: str, is_visible: bool):
    row_no = row_number_by_value(SHEET_DAY_BUTTONS, "id", str(button_id))
    if not row_no:
        return
    ws = worksheet(SHEET_DAY_BUTTONS)
    headers = ws.row_values(1)
    # Keep the day value from the existing row.
    values = ws.row_values(row_no)
    values = values + [""] * (len(headers) - len(values))
    day = values[headers.index("day")]
    row = [
        str(button_id),
        str(day),
        button_text.strip(),
        url.strip() or "#",
        style.strip() or "ghost",
        str(sort_order or "99"),
        "TRUE" if is_visible else "FALSE",
        now_text()
    ]
    ws.update(f"A{row_no}:H{row_no}", [row])
    invalidate_cache()


def delete_day_button(button_id: str):
    row_no = row_number_by_value(SHEET_DAY_BUTTONS, "id", str(button_id))
    if row_no and row_no > 1:
        worksheet(SHEET_DAY_BUTTONS).delete_rows(row_no)
        invalidate_cache()


def list_day_files(day: int) -> List[dict]:
    files = []
    for row in get_records(SHEET_DAY_FILES):
        if str(row.get("day")) == str(day):
            files.append(row)
    return files


def add_day_file(day: int, title: str, url: str):
    ws = worksheet(SHEET_DAY_FILES)
    file_id = str(uuid.uuid4())[:12]
    ws.append_row([file_id, str(day), title.strip(), url.strip(), now_text()])
    invalidate_cache()


def update_day_file(file_id: str, title: str, url: str):
    row_no = row_number_by_value(SHEET_DAY_FILES, "id", str(file_id))
    if not row_no:
        return
    ws = worksheet(SHEET_DAY_FILES)
    headers = ws.row_values(1)
    values = ws.row_values(row_no)
    values = values + [""] * (len(headers) - len(values))
    day = values[headers.index("day")]
    ws.update(f"A{row_no}:E{row_no}", [
              [str(file_id), str(day), title.strip(), url.strip(), now_text()]])
    invalidate_cache()


def delete_day_file(file_id: str):
    row_no = row_number_by_value(SHEET_DAY_FILES, "id", str(file_id))
    if row_no and row_no > 1:
        worksheet(SHEET_DAY_FILES).delete_rows(row_no)
        invalidate_cache()


def upload_to_google_drive(day: int, file_storage, custom_title: str = "") -> dict:
    if not GOOGLE_DRIVE_FOLDER_ID:
        raise ConfigError(
            "GOOGLE_DRIVE_FOLDER_ID is missing. Add it in Vercel/local .env to upload files directly to Google Drive.")
    if not file_storage or not file_storage.filename:
        raise ValueError("No file selected.")

    service = get_drive_service()
    safe_name = secure_filename(file_storage.filename) or "uploaded_file"
    display_title = custom_title.strip() or safe_name
    drive_name = f"Day {day:02d} - {display_title}"
    mime_type = file_storage.mimetype or "application/octet-stream"

    file_bytes = file_storage.read()
    media = MediaIoBaseUpload(io.BytesIO(file_bytes),
                              mimetype=mime_type, resumable=False)
    metadata = {
        "name": drive_name,
        "parents": [GOOGLE_DRIVE_FOLDER_ID]
    }
    created = service.files().create(
        body=metadata,
        media_body=media,
        fields="id,name,webViewLink,webContentLink"
    ).execute()

    try:
        service.permissions().create(
            fileId=created["id"],
            body={"type": "anyone", "role": "reader"},
            fields="id"
        ).execute()
    except Exception:
        # Some Google Workspace policies block public sharing. The admin can still manually share the file/folder.
        pass

    final_file = service.files().get(
        fileId=created["id"],
        fields="id,name,webViewLink,webContentLink"
    ).execute()

    return {
        "id": final_file.get("id"),
        "name": final_file.get("name"),
        "url": final_file.get("webViewLink") or final_file.get("webContentLink") or f"https://drive.google.com/file/d/{created['id']}/view",
        "title": display_title,
    }


def all_student_stages() -> List[dict]:
    students = [u for u in get_records(
        SHEET_USERS) if str(u.get("role")) == "student"]
    rows = []
    for user in students:
        progress, completed, total, percent, xp, level = get_progress_stats(
            user["id"])
        current_day = min(completed + 1, total)
        if completed == total:
            stage = "Completed"
        else:
            stage = f"Day {current_day}"
        rows.append({
            "id": user["id"],
            "name": user.get("name", "Student"),
            "email": user.get("email", ""),
            "avatar": user.get("avatar", "🧑‍💻"),
            "completed": completed,
            "total": total,
            "percent": percent,
            "stage": stage,
            "xp": xp,
            "level": level
        })
    rows.sort(key=lambda x: (-x["completed"], x["name"]))
    return rows


def get_day_setting(day: int) -> dict:
    rows = get_records(SHEET_DAY_SETTINGS)

    for row in rows:
        if str(row.get("day")) == str(day):
            return {
                "day": day,
                "submission_required": str(row.get("submission_required", "")).upper() == "TRUE",
                "submission_title": str(row.get("submission_title", "")) or f"Submit Day {day} Work",
                "submission_help": str(row.get("submission_help", "")) or "Paste your work link or short explanation.",
                "updated_at": str(row.get("updated_at", ""))
            }

    return {
        "day": day,
        "submission_required": False,
        "submission_title": f"Submit Day {day} Work",
        "submission_help": "Paste your work link or short explanation.",
        "updated_at": ""
    }


def update_day_setting(day: int, submission_required: bool, submission_title: str, submission_help: str):
    row_no = row_number_by_value(SHEET_DAY_SETTINGS, "day", str(day))
    ws = worksheet(SHEET_DAY_SETTINGS)

    values = [
        str(day),
        "TRUE" if submission_required else "FALSE",
        submission_title.strip(),
        submission_help.strip(),
        now_text()
    ]

    if row_no:
        ws.update(f"A{row_no}:E{row_no}", [values])
    else:
        ws.append_row(values)

    invalidate_cache()


def get_student_submission(user_id: str, day: int) -> dict:
    rows = get_records(SHEET_SUBMISSIONS)

    for row in rows:
        if str(row.get("user_id")) == str(user_id) and str(row.get("day")) == str(day):
            return {
                "id": str(row.get("id", "")),
                "user_id": str(row.get("user_id", "")),
                "day": str(row.get("day", "")),
                "submission_text": str(row.get("submission_text", "")),
                "submission_url": str(row.get("submission_url", "")),
                "status": str(row.get("status", "")),
                "submitted_at": str(row.get("submitted_at", "")),
                "updated_at": str(row.get("updated_at", ""))
            }

    return {
        "id": "",
        "user_id": str(user_id),
        "day": str(day),
        "submission_text": "",
        "submission_url": "",
        "status": "",
        "submitted_at": "",
        "updated_at": ""
    }


def save_student_submission(user_id: str, day: int, submission_text: str, submission_url: str):
    row_no = row_number_by_two_values(
        SHEET_SUBMISSIONS, "user_id", str(user_id), "day", str(day))
    ws = worksheet(SHEET_SUBMISSIONS)

    existing = get_student_submission(user_id, day)
    submission_id = existing.get("id") or str(uuid.uuid4())[:12]
    submitted_at = existing.get("submitted_at") or now_text()

    values = [
        submission_id,
        str(user_id),
        str(day),
        submission_text.strip(),
        submission_url.strip(),
        "Submitted",
        submitted_at,
        now_text()
    ]

    if row_no:
        ws.update(f"A{row_no}:H{row_no}", [values])
    else:
        ws.append_row(values)

    invalidate_cache()


def has_required_submission(user_id: str, day: int) -> bool:
    submission = get_student_submission(user_id, day)
    return bool(
        submission.get("submission_text", "").strip()
        or submission.get("submission_url", "").strip()
    )


def list_day_submissions(day: int) -> list:
    submissions = []

    for row in get_records(SHEET_SUBMISSIONS):
        if str(row.get("day")) == str(day):
            user = find_user_by_id(str(row.get("user_id", "")))
            submissions.append({
                "id": row.get("id", ""),
                "user_id": row.get("user_id", ""),
                "student_name": user.get("name", "Unknown") if user else "Unknown",
                "student_email": user.get("email", "") if user else "",
                "avatar": user.get("avatar", "🧑‍💻") if user else "🧑‍💻",
                "submission_text": row.get("submission_text", ""),
                "submission_url": row.get("submission_url", ""),
                "status": row.get("status", ""),
                "submitted_at": row.get("submitted_at", ""),
                "updated_at": row.get("updated_at", "")
            })

    return submissions
