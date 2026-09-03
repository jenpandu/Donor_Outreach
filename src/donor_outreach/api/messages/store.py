from donor_outreach.schemas.message import MessageRead, OutboundMessageCreate, InboundMessageCreate, MessageUpdate
from donor_outreach.db_models import Message, Campaign, MessageDirection
from sqlalchemy import select
from donor_outreach.extensions import db
from donor_outreach.clients.translate import TranslateClient
from donor_outreach.clients.comprehend import ComprehendClient
from botocore.exceptions import ClientError
from donor_outreach.errors import NotFoundError
from sqlalchemy import or_


def list_messages(
    campaign_id: int,
    direction: str | None = None,
    language: str | None = None,
    sort: str = "asc",
) -> list[MessageRead]:
    stmt = select(Message).where(Message.campaign_id == campaign_id)

    if direction is not None:
        stmt = stmt.where(Message.direction == direction)

    if language is not None:
        stmt = stmt.where(
            or_(Message.original_language == language, Message.target_language == language)
        )

    if sort == "desc":
        stmt = stmt.order_by(Message.created_at.desc())
    else:
        stmt = stmt.order_by(Message.created_at.asc())

    rows = db.session.execute(stmt)
    return [MessageRead.model_validate(row[0]) for row in rows]

def find_message_by_id(message_id: int) -> MessageRead:
    row = db.session.get(Message, message_id)
    if row is None:
        raise NotFoundError(f"Message {message_id} not found")
    return MessageRead.model_validate(row)


CONFIDENCE_THRESHOLD = 0.5


def create_outbound_message(campaign_id: int, message: dict) -> MessageRead | None:
    campaign = db.session.get(Campaign, campaign_id)
    if campaign is None:
        return None

    valid_message = OutboundMessageCreate.model_validate(message)

    if valid_message.target_language == campaign.def_lang:
        translated_text = valid_message.original_text
    else:
        translator = TranslateClient()
        try:
            translated_text = translator.translate_text(
                text=valid_message.original_text,
                src_lang=campaign.def_lang,
                trg_lang=valid_message.target_language,
            )
        except ClientError:
            translated_text = None

    new_message = Message(
        campaign_id=campaign_id,
        direction=MessageDirection.OUTBOUND,
        donor_name=valid_message.donor_name,
        original_text=valid_message.original_text,
        original_language=campaign.def_lang,
        translated_text=translated_text,
        target_language=valid_message.target_language,
    )
    db.session.add(new_message)
    db.session.commit()
    return MessageRead.model_validate(new_message)


def create_inbound_message(campaign_id: int, message: dict) -> MessageRead | None:
    campaign = db.session.get(Campaign, campaign_id)
    if campaign is None:
        return None

    valid_message = InboundMessageCreate.model_validate(message)

    comprehend = ComprehendClient()
    try:
        detected_language, confidence = comprehend.detect_language(valid_message.original_text)
        if confidence < CONFIDENCE_THRESHOLD:
            detected_language = campaign.def_lang
    except ClientError:
        detected_language = campaign.def_lang

    if detected_language == campaign.def_lang:
        translated_text = valid_message.original_text
    else:
        translator = TranslateClient()
        try:
            translated_text = translator.translate_text(
                text=valid_message.original_text,
                src_lang=detected_language,
                trg_lang=campaign.def_lang,
            )
        except ClientError:
            translated_text = None

    new_message = Message(
        campaign_id=campaign_id,
        direction=MessageDirection.INBOUND,
        donor_name=valid_message.donor_name,
        original_text=valid_message.original_text,
        original_language=detected_language,
        translated_text=translated_text,
        target_language=campaign.def_lang,
    )
    db.session.add(new_message)
    db.session.commit()
    return MessageRead.model_validate(new_message)

def update_message(message_id: int, message: dict) -> MessageRead:
    valid_update = MessageUpdate.model_validate(message)

    record = db.session.get(Message, message_id)
    if record is None:
        raise NotFoundError(f"Message {message_id} not found")

    updates = valid_update.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(record, field, value)

    # Re-trigger translation since original_text changed.
    if "original_text" in updates:
        campaign = record.campaign
        if record.direction == MessageDirection.OUTBOUND:
            source_lang, target_lang = campaign.def_lang, record.target_language
        else:
            comprehend = ComprehendClient()
            try:
                detected_language, confidence = comprehend.detect_language(record.original_text)
                if confidence < CONFIDENCE_THRESHOLD:
                    detected_language = campaign.def_lang
            except ClientError:
                detected_language = campaign.def_lang
            record.original_language = detected_language
            source_lang, target_lang = detected_language, campaign.def_lang

        if source_lang == target_lang:
            record.translated_text = record.original_text
        else:
            translator = TranslateClient()
            try:
                record.translated_text = translator.translate_text(
                    text=record.original_text, src_lang=source_lang, trg_lang=target_lang
                )
            except ClientError:
                record.translated_text = None

    db.session.commit()
    return MessageRead.model_validate(record)

def delete_message(message_id: int) -> None:
    record = db.session.get(Message, message_id)
    if record is None:
        raise NotFoundError(f"Message {message_id} not found")

    db.session.delete(record)
    db.session.commit()


def get_inbox(campaign_id: int) -> list[MessageRead] | None:
    """Return all inbound messages for a campaign, translated at creation
    time. Returns None if the campaign itself doesn't exist.
    """
    campaign = db.session.get(Campaign, campaign_id)
    if campaign is None:
        return None

    stmt = (
        select(Message)
        .where(Message.campaign_id == campaign_id, Message.direction == MessageDirection.INBOUND)
        .order_by(Message.created_at.desc())
    )
    rows = db.session.execute(stmt)
    return [MessageRead.model_validate(row[0]) for row in rows]