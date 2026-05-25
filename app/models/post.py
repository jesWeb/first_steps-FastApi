from __future__ import annotations
from typing import List, TYPE_CHECKING
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Integer, String, Text, DateTime, UniqueConstraint, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

if TYPE_CHECKING:
    from .tag import TagOrm
    from .author import AuthorORM

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey(
        "posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)


class PostORM(Base):
    # decalrar tabla
    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("title", name="unique_post_title"),)
    # declarar columnas
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.astimezone)
    """Relacion uno a nuno """
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("authors.id"))
    author: Mapped[Optional["AuthorORM"]] = relationship(
        back_populates="posts")

    """Relacion muchos a muchos """
    tags: Mapped[List["TagOrm"]] = relationship(
        # realcion con la tabla intermedia
        secondary="post_tags",
        # accede atravez alias
        back_populates="posts",
        # busqueda
        lazy="selectin",
        # borrado cascada
        passive_deletes=True
    )
