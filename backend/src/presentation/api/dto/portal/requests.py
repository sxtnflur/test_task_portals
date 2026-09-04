from pydantic import BaseModel, Field


class PortalIdDTO(BaseModel):
    """Request data identifying a portal aggregate."""

    portal_id: int = Field(gt=0)