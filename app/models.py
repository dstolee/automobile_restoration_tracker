from datetime import date, datetime
from . import db

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    year = db.Column(db.Integer)
    make = db.Column(db.String(80))
    model = db.Column(db.String(80))
    vin = db.Column(db.String(80))
    colour = db.Column(db.String(80))
    cover_filename = db.Column(db.String(255))
    cover_original_filename = db.Column(db.String(255))
    target_description = db.Column(db.Text)
    status = db.Column(db.String(30), default="Planning")
    target_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    jobs = db.relationship("Job", backref="project", cascade="all, delete-orphan")
    parts = db.relationship("Part", backref="project", cascade="all, delete-orphan")
    links = db.relationship("ReferenceLink", backref="project", cascade="all, delete-orphan")
    expenses = db.relationship("Expense", backref="project", cascade="all, delete-orphan")
    notes = db.relationship("ProjectNote", backref="project", cascade="all, delete-orphan")

    @property
    def vehicle_name(self):
        bits = [str(self.year) if self.year else "", self.make or "", self.model or ""]
        return " ".join(x for x in bits if x).strip() or self.name

    @property
    def total_spent(self):
        return sum(float(x.amount or 0) for x in self.expenses)

    @property
    def completion(self):
        if not self.jobs:
            return 0
        done = sum(1 for j in self.jobs if j.status == "Complete")
        return round(done / len(self.jobs) * 100)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    category = db.Column(db.String(60), default="Other")
    status = db.Column(db.String(30), default="Planned")
    priority = db.Column(db.String(20), default="Medium")
    description = db.Column(db.Text)
    procedure = db.Column(db.Text)
    location = db.Column(db.String(120))
    assigned_to = db.Column(db.String(120))
    estimated_hours = db.Column(db.Float)
    actual_hours = db.Column(db.Float)
    estimated_cost = db.Column(db.Numeric(12, 2))
    due_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    photos = db.relationship("Photo", backref="job", cascade="all, delete-orphan")
    parts = db.relationship("Part", backref="job")
    links = db.relationship("ReferenceLink", backref="job")

class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"))
    name = db.Column(db.String(160), nullable=False)
    part_number = db.Column(db.String(100))
    supplier = db.Column(db.String(120))
    url = db.Column(db.String(500))
    quantity = db.Column(db.Integer, default=1)
    unit_cost = db.Column(db.Numeric(12, 2))
    status = db.Column(db.String(30), default="Needed")
    ordered_date = db.Column(db.Date)
    received_date = db.Column(db.Date)
    storage_location = db.Column(db.String(120))
    notes = db.Column(db.Text)

    @property
    def total_cost(self):
        return float(self.unit_cost or 0) * (self.quantity or 0)

class ReferenceLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"))
    title = db.Column(db.String(180), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(60), default="Reference")
    notes = db.Column(db.Text)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    caption = db.Column(db.String(250))
    stage = db.Column(db.String(30), default="Progress")
    taken_date = db.Column(db.Date)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    date = db.Column(db.Date, default=date.today)
    category = db.Column(db.String(60), default="Parts")
    vendor = db.Column(db.String(120))
    description = db.Column(db.String(250), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    receipt_reference = db.Column(db.String(300))

class ProjectNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    body = db.Column(db.Text)
    note_type = db.Column(db.String(40), default="General")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
