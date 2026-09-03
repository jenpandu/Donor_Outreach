from donor_outreach.schemas.campaign import CampaignRead, CampaignCreate, CampaignUpdate, CampaignDashboardRead
from donor_outreach.db_models import Campaign, MessageDirection
from sqlalchemy import select
from donor_outreach.extensions import db
from donor_outreach.errors import NotFoundError


def list_campaigns() -> list[CampaignDashboardRead]:
    stmt = select(Campaign).order_by(Campaign.id)
    rows = db.session.execute(stmt)

    results = []
    for row in rows:
        campaign = row[0]
        outbound_count = sum(1 for m in campaign.messages if m.direction == MessageDirection.OUTBOUND)
        inbound_count = sum(1 for m in campaign.messages if m.direction == MessageDirection.INBOUND)
        results.append(
            CampaignDashboardRead(
                id=campaign.id,
                name=campaign.name,
                goal_amt=campaign.goal_amt,
                description=campaign.description,
                def_lang=campaign.def_lang,
                created_at=campaign.created_at,
                outbound_count=outbound_count,
                inbound_count=inbound_count,
            )
        )
    return results


def find_campaign_by_id(campaign_id: int) -> CampaignRead:
    row = db.session.get(Campaign, campaign_id)
    if row is None:
        raise NotFoundError(f"Campaign {campaign_id} not found")
    return CampaignRead.model_validate(row)

def create_campaign(campaign: dict) -> CampaignRead:
    valid_campaign = CampaignCreate.model_validate(campaign)
    new_campaign = Campaign(**valid_campaign.model_dump())

    db.session.add(new_campaign)
    db.session.commit()

    return CampaignRead.model_validate(new_campaign)


def update_campaign(campaign_id: int, campaign: dict) -> CampaignRead:
    valid_update = CampaignUpdate.model_validate(campaign)

    record = db.session.get(Campaign, campaign_id)
    if record is None:
        raise NotFoundError(f"Campaign {campaign_id} not found")

    updates = valid_update.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(record, field, value)

    db.session.commit()

    return CampaignRead.model_validate(record)

def delete_campaign(campaign_id: int) -> bool:
    record = db.session.get(Campaign, campaign_id)
    if record is None:
        raise NotFoundError(f"Campaign {campaign_id} not found")

    db.session.delete(record)
    db.session.commit()

    return True
