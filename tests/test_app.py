from io import BytesIO

from PIL import Image

from app import db
from app.models import Project


def test_health_check(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_dashboard_empty(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"No projects yet" in response.data


def test_404_page(client):
    response = client.get("/project/99999")
    assert response.status_code == 404
    assert b"Page not found" in response.data


def test_project_creation(client, app):
    response = client.post(
        "/project/new",
        data={
            "name": "Farm Truck",
            "year": "1950",
            "make": "GMC",
            "model": "1-ton",
            "status": "Active",
            "target_description": "Mechanical restoration first.",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Project created" in response.data
    assert b"Farm Truck" in response.data

    with app.app_context():
        project = db.session.execute(db.select(Project)).scalar_one()
        assert project.year == 1950
        assert project.vehicle_name == "1950 GMC 1-ton"
        assert project.completion == 0


def make_cover_image():
    output = BytesIO()
    Image.new("RGB", (320, 180), "gray").save(output, format="JPEG")
    output.seek(0)
    return output


def test_project_cover_image_appears_on_dashboard(client, app):
    response = client.post(
        "/project/new",
        data={
            "name": "Cover Photo Project",
            "year": "1951",
            "make": "International",
            "model": "L-110",
            "cover_image": (make_cover_image(), "truck.jpg"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        project = db.session.execute(db.select(Project)).scalar_one()
        assert project.cover_filename.endswith(".jpg")
        filename = project.cover_filename

    dashboard = client.get("/")
    assert filename.encode() in dashboard.data
    assert b"project cover" in dashboard.data


def test_project_without_cover_uses_placeholder(client):
    client.post("/project/new", data={"name": "No Cover Project"})
    dashboard = client.get("/")
    assert b"Add a project photo" in dashboard.data
