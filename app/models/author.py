from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.core.db import Base


# sirve para imprtaciones circulares -> nos ayuda a evitar errores en el editor de codigo mas no se ejecuta en la ejecucion de codigo 

if TYPE_CHECKING:
    from .post import PostORM


class AuthorORM(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    posts: Mapped[List["PostORM"]] = relationship(back_populates="author")
