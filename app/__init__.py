from datetime import timezone
from zoneinfo import ZoneInfo

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from datetime import timezone
from zoneinfo import ZoneInfo

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix


class ApplicationPrefixMiddleware:
    def __init__(
        self,
        app,
        prefix,
    ):
        self.app = app
        self.prefix = prefix.rstrip("/")

    def __call__(
        self,
        environ,
        start_response,
    ):
        if environ.get("HTTP_X_FORWARDED_HOST"):
            environ["SCRIPT_NAME"] = self.prefix

        return self.app(
            environ,
            start_response,
        )


db = SQLAlchemy()
migrate = Migrate()


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
    )

    app.wsgi_app = ApplicationPrefixMiddleware(
        app.wsgi_app,
        "/symptomtracker",
    )

    from app.i18n import (
        SUPPORTED_LANGUAGES,
        get_current_language,
        translate,
    )

    @app.context_processor
    def inject_i18n():
        return {
            "current_language": (
                get_current_language()
            ),
            "supported_languages": (
                SUPPORTED_LANGUAGES
            ),
            "t": translate,
        }

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
