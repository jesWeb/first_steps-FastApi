from __future__ import annotations
from app.core.db import Base
from app.models.post import PostORM
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import List
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .post import PostORM


class TagORM(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, index=True)

    posts: Mapped[List["PostORM"]] = relationship(
        secondary="post_tags",
        back_populates="tags",
        lazy="selectin"
    )
