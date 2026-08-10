from datetime import timezone
from zoneinfo import ZoneInfo

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)

    from app import models

    migrate.init_app(
        app,
        db,
    )

    @app.template_filter("local_datetime")
    def local_datetime(value):
        if value is None:
            return ""

        if value.tzinfo is None:
            value = value.replace(
                tzinfo=timezone.utc
            )

        local_tz = ZoneInfo(
            app.config["TIMEZONE"]
        )

        local_value = value.astimezone(
            local_tz
        )

        return local_value.strftime(
            "%Y-%m-%d %H:%M"
        )

    @app.template_filter("local_datetime_input")
    def local_datetime_input(value):
        if value is None:
            return ""

        if value.tzinfo is None:
            value = value.replace(
                tzinfo=timezone.utc
            )

        local_tz = ZoneInfo(
            app.config["TIMEZONE"]
        )

        return (
            value
            .astimezone(local_tz)
            .strftime("%Y-%m-%dT%H:%M")
        )

    from app.routes import main

    app.register_blueprint(main)

    return app
