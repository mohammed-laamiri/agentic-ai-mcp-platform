# app/models/base.py

"""
Base SQLModel Metadata Layer.

Purpose:
- Provide a single base for all SQLModel models
- Include common fields like `id`, `created_at`, `updated_at`
- Keep all models consistent
- Prepare for Task, Agent, Tool, RAG metadata
"""

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class BaseModel(SQLModel):
    """
    Base model for all database entities.

    Fields:
    - id: primary key
    - created_at: timestamp of creation
    - updated_at: timestamp of last update
    """

    id: Optional[str] = Field(
        default=None, primary_key=True, index=True, description="Unique ID of the entity"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp of creation",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Timestamp of last update",
    )

    def update_timestamp(self) -> None:
        """
        Updates the `updated_at` timestamp.

        Should be called before saving changes to the DB.
        """
        self.updated_at = datetime.utcnow()
