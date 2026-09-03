from flask import Blueprint, jsonify, request
from donor_outreach.api.campaigns import store
from donor_outreach.responses import list_envelope, single_envelope

campaigns_bp = Blueprint("campaigns", __name__ )

@campaigns_bp.get("")
def get_campaigns():
    return list_envelope(store.list_campaigns())

@campaigns_bp.get("/<int:campaign_id>")
def get_campaigns_by_id(campaign_id):
    campaign = store.find_campaign_by_id(campaign_id)
    return single_envelope(campaign)

@campaigns_bp.post("")
def create_new_campaign():
    body = request.get_json(silent=True) or {}
    return single_envelope(store.create_campaign(body)), 201

@campaigns_bp.put("/<int:campaign_id>")
def update_campaign(campaign_id: int):
    body = request.get_json(silent=True) or {}
    updated = store.update_campaign(campaign_id, body)
    return single_envelope(updated), 200

@campaigns_bp.delete("/<int:campaign_id>")
def delete_campaign(campaign_id: int):
    store.delete_campaign(campaign_id)
    return jsonify(status="deleted"), 204

    






