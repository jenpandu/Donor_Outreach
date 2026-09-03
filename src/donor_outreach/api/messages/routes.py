from flask import Blueprint, jsonify, request

from donor_outreach.api.messages import store
from donor_outreach.responses import list_envelope, single_envelope

messages_bp = Blueprint("messages", __name__)


@messages_bp.get("/campaigns/<int:campaign_id>/messages")
def get_messages(campaign_id: int):
    direction = request.args.get("direction")
    language = request.args.get("language")
    sort = request.args.get("sort", "asc")
    return list_envelope(store.list_messages(campaign_id, direction=direction, language=language, sort=sort))


@messages_bp.get("/messages/<int:message_id>")
def get_message_by_id(message_id: int):
    message = store.find_message_by_id(message_id)
    return single_envelope(message)


@messages_bp.post("/campaigns/<int:campaign_id>/messages/outbound")
def create_outbound_message_route(campaign_id: int):
    body = request.get_json(silent=True) or {}
    ob_message = store.create_outbound_message(campaign_id, body)
    if ob_message is None:
        return jsonify(error="not_found", detail=f"Campaign {campaign_id} not found"), 404
    return single_envelope(ob_message), 201


@messages_bp.post("/campaigns/<int:campaign_id>/messages/inbound")
def create_inbound_message_route(campaign_id: int):
    body = request.get_json(silent=True) or {}
    ib_message = store.create_inbound_message(campaign_id, body)
    if ib_message is None:
        return jsonify(error="not_found", detail=f"Campaign {campaign_id} not found"), 404
    return single_envelope(ib_message), 201


@messages_bp.put("/messages/<int:message_id>")
def update_message_route(message_id: int):
    body = request.get_json(silent=True) or {}
    updated = store.update_message(message_id, body)
    return single_envelope(updated)



@messages_bp.delete("/messages/<int:message_id>")
def delete_message_route(message_id: int):
    store.delete_message(message_id)
    return jsonify(status="deleted"), 204

@messages_bp.get("/campaigns/<int:campaign_id>/inbox")
def get_inbox(campaign_id: int):
    inbox = store.get_inbox(campaign_id)
    if inbox is None:
        return jsonify(error="not_found", detail=f"Campaign {campaign_id} not found"), 404

    if not inbox:
        return jsonify(message="Inbox is empty", count=0, items=[]), 200

    return list_envelope(inbox)