from flask import Flask, jsonify
from flask_migrate import Migrate
from donor_outreach import db_models
from donor_outreach.config import get_settings
from donor_outreach.api.health import health_bp
from donor_outreach.api.campaigns.routes import campaigns_bp
from donor_outreach.api.messages.routes import messages_bp
from pydantic import ValidationError
from donor_outreach.extensions import db
from donor_outreach.errors import DomainError
from donor_outreach.responses import error_response
import uuid
import time

import structlog
from flask import Flask, g, request

from donor_outreach.logging_config import configure_logging

logger = structlog.get_logger()

migrate = Migrate()

def create_app() -> Flask:
    settings = get_settings()
    configure_logging(settings.log_level)
    app = Flask(__name__)



    app.config["LOG_LEVEL"] = settings.log_level
    # establishing db connection
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # grabbing the url value from the .env
    app.register_blueprint(health_bp)
    app.register_blueprint(campaigns_bp, url_prefix="/campaigns")
    app.register_blueprint(messages_bp)
    db.init_app(app)                                                    # initializing db with flask
    
    migrate.init_app(app, db)                                           # helps to manage tables in db
    
    @app.errorhandler(DomainError)
    def handle_domain_error(err: DomainError):
        return error_response(err)

    @app.errorhandler(ValidationError)
    def handle_validation_error(err: ValidationError):
        return jsonify(error ="validation_failed", detail=err.errors()), 422

    
    @app.before_request
    def bind_request_context():
        g.request_id = str(uuid.uuid4())
        g.request_start_time = time.monotonic()
        structlog.contextvars.bind_contextvars(request_id=g.request_id)

    @app.after_request
    def log_request(response):
        duration_ms = round((time.monotonic() - g.request_start_time) * 1000, 2)
        logger.info(
            "request_handled",
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        structlog.contextvars.clear_contextvars()
        return response


    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)