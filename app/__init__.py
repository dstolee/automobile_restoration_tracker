from pathlib import Path

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import inspect, text

from config import Config

db = SQLAlchemy()
csrf = CSRFProtect()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    csrf.init_app(app)

    from .routes import bp

    app.register_blueprint(bp)

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    @app.errorhandler(413)
    def upload_too_large(_error):
        return render_template("413.html"), 413

    with app.app_context():
        db.create_all()
        # Lightweight compatibility migration for installations created before
        # project cover images were introduced. A formal migration framework is
        # planned, but these nullable columns are safe to add in place.
        columns = {column["name"] for column in inspect(db.engine).get_columns("project")}
        if "cover_filename" not in columns:
            db.session.execute(text("ALTER TABLE project ADD COLUMN cover_filename VARCHAR(255)"))
        if "cover_original_filename" not in columns:
            db.session.execute(
                text("ALTER TABLE project ADD COLUMN cover_original_filename VARCHAR(255)")
            )
        db.session.commit()

    return app
