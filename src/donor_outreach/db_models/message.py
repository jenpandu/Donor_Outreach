
from sqlalchemy import ForeignKey, String, Numeric, Enum, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from donor_outreach.extensions import db
import enum
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from donor_outreach.db_models.campaign import Campaign

class MessageDirection(str, enum.Enum):
    OUTBOUND = "outbound"
    INBOUND = "inbound"
class Message(db.Model):
    
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False
    )
    direction: Mapped[MessageDirection] = mapped_column(
        Enum(MessageDirection, name="message_direction"), nullable=False
    )
    donor_name: Mapped[str] = mapped_column(String(20), nullable=False)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    original_language: Mapped[str] = mapped_column(String(15), nullable=False)

    translated_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_language: Mapped[str] = mapped_column(String(10), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    campaign: Mapped["Campaign"] = relationship(back_populates="messages")

