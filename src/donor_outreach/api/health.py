from flask import Blueprint, jsonify
from sqlalchemy import text
from donor_outreach.extensions import db

health_bp = Blueprint("health", __name__)

@health_bp.route("/live")
def live():
    return {"status": "ok"}, 200

@health_bp.get("/ready")
def ready():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify(status="ready"), 200

    except Exception:
        return jsonify(status="not_ready", detail="database unreachable"), 503
