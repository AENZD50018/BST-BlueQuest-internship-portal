from sheets_store import ConfigError
import sheets_store as store
from days import DAYS, get_day
from flask import (
    Flask, render_template, request, redirect, url_for, session,
    flash, Response, send_from_directory
)
from functools import wraps
import os
import time

from dotenv import load_dotenv

load_dotenv()


_LAST_INIT_TIME = 0
_INIT_DONE = False
_INIT_ERROR = None


app = Flask(__name__, static_folder="public", static_url_path="")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-this")
app.config["SESSION_COOKIE_NAME"] = "bst_bluequest_gsheets_session"

AVATARS = ["🧑‍💻", "👩‍💻", "🧙", "🧠", "🚀", "🐱‍💻", "🛡️", "⚡"]


def safe_initialize(force=False):
    global _LAST_INIT_TIME, _INIT_DONE, _INIT_ERROR

    now = time.time()

    # Do not initialize again and again.
    # This avoids Google Sheets quota error.
    if not force and _INIT_DONE and (now - _LAST_INIT_TIME) < 600:
        return None

    try:
        store.initialize_sheet()
        _INIT_DONE = True
        _INIT_ERROR = None
        _LAST_INIT_TIME = now
        return None

    except ConfigError as exc:
        _INIT_DONE = False
        _INIT_ERROR = str(exc)
        _LAST_INIT_TIME = now
        return str(exc)

    except Exception as exc:
        _INIT_DONE = False
        _INIT_ERROR = "Google Sheets connection failed: " + str(exc)
        _LAST_INIT_TIME = now
        return _INIT_ERROR


@app.before_request
def before_request():
    allowed = {"setup", "static_css", "landing"}
    if request.endpoint in allowed:
        return
    err = safe_initialize()
    if err:
        return render_template(
            "setup_error.html",
            error=err,
            service_email=store.get_service_account_email()
        ), 500


@app.route("/css/<path:filename>")
def static_css(filename):
    return send_from_directory("public/css", filename)


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = store.find_user_by_id(user_id)
    if not user:
        session.clear()
        return None
    return user


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user:
            flash("Please login again.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user:
            flash("Please login again.", "warning")
            return redirect(url_for("login"))
        if user.get("role") != "admin":
            flash("Admin permission required.", "danger")
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_logged_user():
    try:
        return {"logged_user": current_user()}
    except Exception:
        return {"logged_user": None}


@app.route("/setup")
def setup():
    err = safe_initialize()
    if err:
        return render_template(
            "setup_error.html",
            error=err,
            service_email=store.get_service_account_email()
        )
    return render_template("setup_success.html")


@app.route("/")
def landing():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        avatar = request.form.get("avatar", "🧑‍💻")

        if not name or not email or not password:
            flash("Please fill all fields.", "danger")
            return redirect(url_for("register"))

        try:
            user = store.create_user(
                email=email, password=password, name=name, role="student", avatar=avatar)
            session["user_id"] = user["id"]
            flash("Account created successfully.", "success")
            return redirect(url_for("dashboard"))
        except ValueError as exc:
            flash(str(exc), "danger")
        except Exception as exc:
            flash("Account could not be created: " + str(exc), "danger")

    return render_template("register.html", avatars=AVATARS)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = store.authenticate(email, password)
        if user:
            session["user_id"] = user["id"]
            flash("Login successful.", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("login"))


@app.route("/reset-session")
def reset_session():
    session.clear()
    flash("Session cleared. Please login again.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    progress, completed_days, total_days, percent, xp, level = store.get_progress_stats(
        user["id"])
    classmates = store.all_student_stages()
    return render_template(
        "dashboard.html",
        user=user,
        days=DAYS,
        progress=progress,
        completed_days=completed_days,
        total_days=total_days,
        percent=percent,
        xp=xp,
        level=level,
        classmates=classmates
    )


@app.route("/day/<int:day_no>", methods=["GET", "POST"])
@login_required
def day_detail(day_no):
    user = current_user()
    day = get_day(day_no)
    if not day:
        flash("Invalid day.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        note = request.form.get("student_note", "")
        store.save_student_note(user["id"], day_no, note)
        flash("Your note was saved.", "success")
        return redirect(url_for("day_detail", day_no=day_no))

    progress = store.get_progress(user["id"])
    student_note = store.get_student_note(user["id"], day_no)
    trainer_note = store.get_day_note(day_no)
    files = store.list_day_files(day_no)
    quick_buttons = store.list_day_buttons(day_no)
    day_setting = store.get_day_setting(day_no)
    submission = store.get_student_submission(user["id"], day_no)
    submission_done = store.has_required_submission(user["id"], day_no)
    return render_template(
        "day_detail.html",
        user=user,
        day=day,
        trainer_note=trainer_note,
        files=files,
        quick_buttons=quick_buttons,
        completed=progress.get(day_no, False),
        student_note=student_note,
        day_setting=day_setting,
        submission=submission,
        submission_done=submission_done
    )


@app.route("/day/<int:day_no>/complete", methods=["POST"])
@login_required
def mark_complete(day_no):
    day_setting = store.get_day_setting(day_no)

    if day_setting.get("submission_required"):
        if not store.has_required_submission(user["id"], day_no):
            flash(
                "Please submit your daily work before marking this day complete.", "warning")
            return redirect(url_for("day_detail", day_no=day_no))
    user = current_user()
    completed = request.form.get("completed") == "on"
    store.set_progress(user["id"], day_no, completed)
    flash("Progress updated.", "success")
    return redirect(url_for("day_detail", day_no=day_no))


@app.route("/download/day/<int:day_no>/notes")
@login_required
def download_day_notes(day_no):
    note = store.get_day_note(day_no)
    filename = f"day{day_no:02d}_updated_notes.md"
    return Response(
        note["content"],
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.route("/download/day/<int:day_no>/original")
@login_required
def download_original_day_notes(day_no):
    note = store.get_original_day_note(day_no)
    filename = f"day{day_no:02d}_original_notes.md"
    return Response(
        note["content"],
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.route("/day/<int:day_no>/submit-work", methods=["POST"])
@login_required
def submit_work(day_no):
    user = current_user()
    if not user:
        session.clear()
        return redirect(url_for("login"))

    submission_text = request.form.get("submission_text", "")
    submission_url = request.form.get("submission_url", "")

    if not submission_text.strip() and not submission_url.strip():
        flash("Please add your work note or work link before submitting.", "warning")
        return redirect(url_for("day_detail", day_no=day_no))

    store.save_student_submission(
        user_id=user["id"],
        day=day_no,
        submission_text=submission_text,
        submission_url=submission_url
    )

    flash("Your work submission has been saved.", "success")
    return redirect(url_for("day_detail", day_no=day_no))


@app.route("/admin")
@admin_required
def admin():
    students = store.all_student_stages()
    return render_template("admin.html", user=current_user(), days=DAYS, students=students, sheet_config=store.get_sheet_config_for_admin())


@app.route("/admin/day/<int:day_no>", methods=["GET", "POST"])
@admin_required
def admin_day(day_no):
    day = get_day(day_no)
    if not day:
        flash("Invalid day.", "danger")
        return redirect(url_for("admin"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_notes":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            content = request.form.get("content", "")
            store.update_day_note(day_no, title, description, content)
            flash("Day notes updated.", "success")

        elif action == "add_file":
            file_title = request.form.get("file_title", "").strip()
            file_url = request.form.get("file_url", "").strip()
            if file_title and file_url:
                store.add_day_file(day_no, file_title, file_url)
                flash("File link added.", "success")
            else:
                flash("File title and URL are required.", "danger")

        elif action == "update_file":
            file_id = request.form.get("file_id", "").strip()
            file_title = request.form.get("file_title", "").strip()
            file_url = request.form.get("file_url", "").strip()
            if file_id and file_title and file_url:
                store.update_day_file(file_id, file_title, file_url)
                flash("File link updated.", "success")
            else:
                flash("File title and URL are required.", "danger")

        elif action == "upload_drive_file":
            upload = request.files.get("drive_file")
            file_title = request.form.get("drive_file_title", "").strip()
            try:
                uploaded = store.upload_to_google_drive(
                    day_no, upload, file_title)
                store.add_day_file(day_no, uploaded["title"], uploaded["url"])
                flash(
                    "File uploaded to Google Drive and added to student downloads.", "success")
            except Exception as exc:
                flash("Google Drive upload failed: " + str(exc), "danger")

        elif action == "add_button":
            button_text = request.form.get("button_text", "").strip()
            button_url = request.form.get("button_url", "").strip()
            style = request.form.get("button_style", "ghost")
            sort_order = request.form.get("sort_order", "99")
            is_visible = request.form.get("is_visible") == "on"
            if button_text:
                store.add_day_button(
                    day_no, button_text, button_url or "#", style, sort_order, is_visible)
                flash("Button added.", "success")
            else:
                flash("Button text is required.", "danger")

        elif action == "update_button":
            button_id = request.form.get("button_id", "").strip()
            button_text = request.form.get("button_text", "").strip()
            button_url = request.form.get("button_url", "").strip()
            style = request.form.get("button_style", "ghost")
            sort_order = request.form.get("sort_order", "99")
            is_visible = request.form.get("is_visible") == "on"
            if button_id and button_text:
                store.update_day_button(
                    button_id, button_text, button_url or "#", style, sort_order, is_visible)
                flash("Button updated.", "success")
            else:
                flash("Button text is required.", "danger")

        elif action == "delete_button":
            button_id = request.form.get("button_id", "").strip()
            if button_id:
                store.delete_day_button(button_id)
                flash("Button deleted.", "success")

        elif action == "update_day_setting":
            submission_required = request.form.get(
                "submission_required") == "on"
            submission_title = request.form.get("submission_title", "")
            submission_help = request.form.get("submission_help", "")

            store.update_day_setting(
                day=day_no,
                submission_required=submission_required,
                submission_title=submission_title,
                submission_help=submission_help
            )

            flash("Day submission setting updated.", "success")

        return redirect(url_for("admin_day", day_no=day_no))

    note = store.get_day_note(day_no)
    files = store.list_day_files(day_no)
    quick_buttons = store.list_day_buttons(day_no)
    day_setting = store.get_day_setting(day_no)
    submissions = store.list_day_submissions(day_no)
    return render_template(
        "admin_day.html",
        user=current_user(),
        day=day,
        note=note,
        files=files,
        quick_buttons=quick_buttons,
        sheet_config=store.get_sheet_config_for_admin(),
        day_setting=day_setting,
        submissions=submissions,
    )


@app.route("/admin/file/<file_id>/delete", methods=["POST"])
@admin_required
def delete_file(file_id):
    day_no = request.form.get("day_no", "1")
    store.delete_day_file(file_id)
    flash("File link deleted.", "success")
    return redirect(url_for("admin_day", day_no=day_no))


if __name__ == "__main__":
    app.run(debug=True)
