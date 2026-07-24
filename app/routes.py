\
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from PIL import Image
from flask import (
    Blueprint, current_app, flash, jsonify, redirect, render_template,
    request, send_from_directory, url_for
)
from sqlalchemy import or_
from werkzeug.utils import secure_filename
from . import db
from .models import Project, Job, Part, ReferenceLink, Photo, Expense, ProjectNote

bp = Blueprint("main", __name__)

JOB_CATEGORIES = [
    "Body", "Paint", "Engine", "Fuel", "Cooling", "Electrical", "Transmission",
    "Driveline", "Brakes", "Steering", "Suspension", "Wheels/Tires",
    "Interior", "Glass", "Trim", "Documentation", "Inspection", "Other"
]
JOB_STATUSES = ["Planned", "Ready", "In Progress", "Blocked", "Complete", "Deferred"]
PART_STATUSES = ["Needed", "Researching", "Ordered", "Received", "Installed", "Returned"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]

def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date() if value else None

def parse_float(value):
    try:
        return float(value) if value not in (None, "") else None
    except ValueError:
        return None

def save_image(file):
    if not file or not file.filename:
        return None
    original = secure_filename(file.filename)
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    if ext not in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        raise ValueError("Only JPG, PNG, and WebP images are allowed.")

    # Verify actual image content, not just the extension.
    file.stream.seek(0)
    with Image.open(file.stream) as img:
        img.verify()
    file.stream.seek(0)

    filename = f"{uuid4().hex}.{ext}"
    destination = Path(current_app.config["UPLOAD_FOLDER"]) / filename
    file.save(destination)
    return filename, original

@bp.context_processor
def inject_options():
    return dict(
        job_categories=JOB_CATEGORIES, job_statuses=JOB_STATUSES,
        part_statuses=PART_STATUSES, priorities=PRIORITIES
    )

@bp.route("/healthz")
def healthz():
    return jsonify(status="ok")


@bp.route("/")
def dashboard():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    upcoming = Job.query.filter(
        Job.status != "Complete", Job.due_date.isnot(None)
    ).order_by(Job.due_date.asc()).limit(10).all()
    blocked = Job.query.filter_by(status="Blocked").order_by(Job.created_at.desc()).limit(10).all()
    return render_template("dashboard.html", projects=projects, upcoming=upcoming, blocked=blocked)

def update_project_from_form(project):
    project.name = request.form["name"].strip()
    project.year = int(request.form["year"]) if request.form.get("year") else None
    project.make = request.form.get("make")
    project.model = request.form.get("model")
    project.vin = request.form.get("vin")
    project.colour = request.form.get("colour")
    project.status = request.form.get("status", "Planning")
    project.target_description = request.form.get("target_description")
    project.target_date = parse_date(request.form.get("target_date"))


def remove_uploaded_image(filename):
    if not filename:
        return
    path = Path(current_app.config["UPLOAD_FOLDER"]) / filename
    if path.exists():
        path.unlink()


def update_project_cover(project):
    if request.form.get("remove_cover") == "1":
        remove_uploaded_image(project.cover_filename)
        project.cover_filename = None
        project.cover_original_filename = None

    uploaded = request.files.get("cover_image")
    if uploaded and uploaded.filename:
        saved = save_image(uploaded)
        if saved:
            new_filename, original_filename = saved
            old_filename = project.cover_filename
            project.cover_filename = new_filename
            project.cover_original_filename = original_filename
            if old_filename and old_filename != new_filename:
                remove_uploaded_image(old_filename)


@bp.route("/project/new", methods=["GET", "POST"])
def project_new():
    if request.method == "POST":
        p = Project()
        try:
            update_project_from_form(p)
            update_project_cover(p)
            db.session.add(p)
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            flash(f"Project was not created: {exc}", "danger")
            return render_template("project_form.html", project=p), 400
        flash("Project created.", "success")
        return redirect(url_for("main.project_detail", project_id=p.id))
    return render_template("project_form.html", project=None)

@bp.route("/project/<int:project_id>")
def project_detail(project_id):
    p = Project.query.get_or_404(project_id)
    q = request.args.get("q", "").strip()
    jobs_query = Job.query.filter_by(project_id=p.id)
    if q:
        jobs_query = jobs_query.filter(or_(Job.title.ilike(f"%{q}%"), Job.description.ilike(f"%{q}%")))
    jobs = jobs_query.order_by(Job.sort_order, Job.due_date, Job.title).all()
    return render_template("project_detail.html", project=p, jobs=jobs, q=q)

@bp.route("/project/<int:project_id>/edit", methods=["GET", "POST"])
def project_edit(project_id):
    p = Project.query.get_or_404(project_id)
    if request.method == "POST":
        try:
            update_project_from_form(p)
            update_project_cover(p)
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            flash(f"Project was not updated: {exc}", "danger")
            return render_template("project_form.html", project=p), 400
        flash("Project updated.", "success")
        return redirect(url_for("main.project_detail", project_id=p.id))
    return render_template("project_form.html", project=p)

@bp.route("/project/<int:project_id>/job/new", methods=["GET", "POST"])
def job_new(project_id):
    p = Project.query.get_or_404(project_id)
    if request.method == "POST":
        j = Job(project_id=p.id)
        update_job_from_form(j)
        db.session.add(j)
        db.session.commit()
        flash("Work item added.", "success")
        return redirect(url_for("main.job_detail", job_id=j.id))
    return render_template("job_form.html", project=p, job=None)

def update_job_from_form(j):
    j.title = request.form["title"].strip()
    j.category = request.form.get("category")
    j.status = request.form.get("status")
    j.priority = request.form.get("priority")
    j.description = request.form.get("description")
    j.procedure = request.form.get("procedure")
    j.location = request.form.get("location")
    j.assigned_to = request.form.get("assigned_to")
    j.estimated_hours = parse_float(request.form.get("estimated_hours"))
    j.actual_hours = parse_float(request.form.get("actual_hours"))
    j.estimated_cost = parse_float(request.form.get("estimated_cost"))
    j.due_date = parse_date(request.form.get("due_date"))
    j.completed_date = parse_date(request.form.get("completed_date"))

@bp.route("/job/<int:job_id>")
def job_detail(job_id):
    return render_template("job_detail.html", job=Job.query.get_or_404(job_id))

@bp.route("/job/<int:job_id>/edit", methods=["GET", "POST"])
def job_edit(job_id):
    j = Job.query.get_or_404(job_id)
    if request.method == "POST":
        update_job_from_form(j)
        db.session.commit()
        flash("Work item updated.", "success")
        return redirect(url_for("main.job_detail", job_id=j.id))
    return render_template("job_form.html", project=j.project, job=j)

@bp.route("/job/<int:job_id>/photo", methods=["POST"])
def photo_add(job_id):
    j = Job.query.get_or_404(job_id)
    try:
        saved = save_image(request.files.get("photo"))
        if not saved:
            raise ValueError("Choose an image first.")
        filename, original = saved
        photo = Photo(
            job_id=j.id, filename=filename, original_filename=original,
            caption=request.form.get("caption"),
            stage=request.form.get("stage", "Progress"),
            taken_date=parse_date(request.form.get("taken_date"))
        )
        db.session.add(photo)
        db.session.commit()
        flash("Photo uploaded.", "success")
    except Exception as exc:
        flash(f"Photo was not uploaded: {exc}", "danger")
    return redirect(url_for("main.job_detail", job_id=j.id))

@bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)

@bp.route("/photo/<int:photo_id>/delete", methods=["POST"])
def photo_delete(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    job_id = photo.job_id
    path = Path(current_app.config["UPLOAD_FOLDER"]) / photo.filename
    if path.exists():
        path.unlink()
    db.session.delete(photo)
    db.session.commit()
    flash("Photo deleted.", "success")
    return redirect(url_for("main.job_detail", job_id=job_id))

@bp.route("/project/<int:project_id>/part", methods=["POST"])
def part_add(project_id):
    p = Project.query.get_or_404(project_id)
    part = Part(
        project_id=p.id,
        job_id=int(request.form["job_id"]) if request.form.get("job_id") else None,
        name=request.form["name"].strip(),
        part_number=request.form.get("part_number"),
        supplier=request.form.get("supplier"),
        url=request.form.get("url"),
        quantity=int(request.form.get("quantity") or 1),
        unit_cost=parse_float(request.form.get("unit_cost")),
        status=request.form.get("status", "Needed"),
        storage_location=request.form.get("storage_location"),
        notes=request.form.get("notes")
    )
    db.session.add(part)
    db.session.commit()
    flash("Part added.", "success")
    return redirect(url_for("main.project_detail", project_id=p.id) + "#parts")

@bp.route("/part/<int:part_id>/edit", methods=["POST"])
def part_edit(part_id):
    part = Part.query.get_or_404(part_id)
    part.status = request.form.get("status", part.status)
    part.quantity = int(request.form.get("quantity") or part.quantity or 1)
    part.unit_cost = parse_float(request.form.get("unit_cost"))
    part.storage_location = request.form.get("storage_location")
    part.notes = request.form.get("notes")
    if part.status == "Received" and not part.received_date:
        part.received_date = datetime.utcnow().date()
    db.session.commit()
    flash("Part updated.", "success")
    return redirect(url_for("main.project_detail", project_id=part.project_id) + "#parts")

@bp.route("/project/<int:project_id>/link", methods=["POST"])
def link_add(project_id):
    p = Project.query.get_or_404(project_id)
    link = ReferenceLink(
        project_id=p.id,
        job_id=int(request.form["job_id"]) if request.form.get("job_id") else None,
        title=request.form["title"].strip(),
        url=request.form["url"].strip(),
        category=request.form.get("category", "Reference"),
        notes=request.form.get("notes")
    )
    db.session.add(link)
    db.session.commit()
    flash("Reference link added.", "success")
    return redirect(url_for("main.project_detail", project_id=p.id) + "#links")

@bp.route("/project/<int:project_id>/expense", methods=["POST"])
def expense_add(project_id):
    p = Project.query.get_or_404(project_id)
    e = Expense(
        project_id=p.id,
        date=parse_date(request.form.get("date")) or datetime.utcnow().date(),
        category=request.form.get("category", "Parts"),
        vendor=request.form.get("vendor"),
        description=request.form["description"].strip(),
        amount=parse_float(request.form.get("amount")) or 0,
        receipt_reference=request.form.get("receipt_reference")
    )
    db.session.add(e)
    db.session.commit()
    flash("Expense added.", "success")
    return redirect(url_for("main.project_detail", project_id=p.id) + "#expenses")

@bp.route("/project/<int:project_id>/note", methods=["POST"])
def note_add(project_id):
    p = Project.query.get_or_404(project_id)
    note = ProjectNote(
        project_id=p.id,
        title=request.form["title"].strip(),
        body=request.form.get("body"),
        note_type=request.form.get("note_type", "General")
    )
    db.session.add(note)
    db.session.commit()
    flash("Note added.", "success")
    return redirect(url_for("main.project_detail", project_id=p.id) + "#notes")
