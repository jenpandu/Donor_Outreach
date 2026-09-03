from pydantic import BaseModel, Field
from typing import Literal, Optional
from sqlalchemy import ForeignKey, String, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from donor_outreach.extensions import db
from typing import TYPE_CHECKING

from datetime import datetime

if TYPE_CHECKING:
    from donor_outreach.db_models.message import Message
"""
SQL Alchemy ORM Models
    - object relational mapping
    - 1:1 map your object properties to columns in a db
    - they also map related entities
    - give default functionality for db interactions

"""


class Campaign(db.Model):


    #name of corresponding db table
    __tablename__ = "campaigns"

    # mapped_colum defines contraints
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20),nullable=False)
    goal_amt: Mapped[float] = mapped_column(Numeric(12,2), nullable=False)
    description: Mapped[str] = mapped_column(String(100), nullable=False)
    def_lang: Mapped[str] = mapped_column(String(5), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()

    )

    messages: Mapped[list["Message"]] = relationship(
    back_populates="campaign", cascade="all, delete-orphan"
)