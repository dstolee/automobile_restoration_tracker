from io import BytesIO

from PIL import Image

from app import db
from app.models import Expense, Job, Part, Photo, Project, ProjectNote, ReferenceLink


def create_project(client):
    client.post(
        "/project/new",
        data={"name": "Test Project", "year": "1967", "make": "MG", "model": "B"},
    )
    return 1


def make_png():
    output = BytesIO()
    Image.new("RGB", (16, 16), "white").save(output, format="PNG")
    output.seek(0)
    return output


def test_full_restoration_workflow(client, app):
    project_id = create_project(client)

    response = client.post(
        f"/project/{project_id}/job/new",
        data={
            "title": "Rebuild front brakes",
            "category": "Brakes",
            "status": "In Progress",
            "priority": "High",
            "estimated_hours": "8.5",
            "estimated_cost": "450.00",
            "description": "Replace cylinders, shoes, hoses, and fluid.",
        },
        follow_redirects=True,
    )
    assert b"Work item added" in response.data
    assert b"Rebuild front brakes" in response.data

    client.post(
        f"/project/{project_id}/part",
        data={
            "name": "Wheel cylinder",
            "part_number": "WC-123",
            "quantity": "2",
            "unit_cost": "45.50",
            "status": "Needed",
            "job_id": "1",
        },
    )
    client.post(
        f"/project/{project_id}/link",
        data={
            "title": "Workshop manual",
            "url": "https://example.com/manual",
            "category": "Manual",
            "job_id": "1",
        },
    )
    client.post(
        f"/project/{project_id}/expense",
        data={"description": "Brake parts", "amount": "91.00", "category": "Parts"},
    )
    client.post(
        f"/project/{project_id}/note",
        data={"title": "Drum limit", "body": "Maximum diameter recorded.", "note_type": "Measurement"},
    )
    response = client.post(
        "/job/1/photo",
        data={
            "photo": (make_png(), "before.png"),
            "stage": "Before",
            "caption": "Before disassembly",
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert b"Photo uploaded" in response.data

    with app.app_context():
        project = db.session.get(Project, project_id)
        assert db.session.execute(db.select(Job)).scalar_one().estimated_hours == 8.5
        assert db.session.execute(db.select(Part)).scalar_one().total_cost == 91.0
        assert db.session.execute(db.select(ReferenceLink)).scalar_one().category == "Manual"
        assert float(db.session.execute(db.select(Expense)).scalar_one().amount) == 91.0
        assert db.session.execute(db.select(ProjectNote)).scalar_one().note_type == "Measurement"
        photo = db.session.execute(db.select(Photo)).scalar_one()
        assert photo.stage == "Before"
        assert (app.config["UPLOAD_FOLDER"] and photo.filename)
        assert project.total_spent == 91.0

    response = client.post("/photo/1/delete", follow_redirects=True)
    assert b"Photo deleted" in response.data
    with app.app_context():
        assert db.session.get(Photo, 1) is None


def test_rejects_non_image_upload(client):
    create_project(client)
    client.post(
        "/project/1/job/new",
        data={"title": "Inspect body", "category": "Body", "status": "Planned", "priority": "Medium"},
    )
    response = client.post(
        "/job/1/photo",
        data={"photo": (BytesIO(b"not an image"), "fake.jpg")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert b"Photo was not uploaded" in response.data
