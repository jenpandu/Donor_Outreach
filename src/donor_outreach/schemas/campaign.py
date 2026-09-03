from pydantic import BaseModel, Field
from datetime import datetime

class CampaignCreate(BaseModel):
    name: str = Field(min_length=1, max_length=20)
    goal_amt: float = Field(gt=0)
    description: str = Field(min_length=1, max_length=100)
    def_lang: str = Field(min_length=2, max_length=20)

class CampaignUpdate(BaseModel):
    """Fields allowed when editing a campaign — all optional (partial update)."""

    name: str | None = Field(default=None, min_length=1, max_length=20)
    goal_amt: float | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, min_length=1, max_length=100)


class CampaignRead(BaseModel):
    """Shape returned to the client when reading a campaign."""

    id: int
    name: str
    goal_amt: float
    description: str
    def_lang: str
    created_at: datetime

    model_config = {"from_attributes": True}

class CampaignDashboardRead(BaseModel):
    id: int
    name: str
    goal_amt: float
    description: str
    def_lang: str
    created_at: datetime
    outbound_count: int
    inbound_count: int

    model_config = {"from_attributes": True}

    