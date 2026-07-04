from __future__ import annotations

from typing import Iterable, Sequence
from collections.abc import Iterable as IterableABC

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.category import CategoryOrm


class CategoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_many(self, *, skip: int = 0, limit: int = 50) -> Sequence[CategoryOrm]:
        query = (select(CategoryOrm).offset(skip).limit(limit))
        return self.db.execute(query).scalars().all()

    def list_with_total(self, *, page: int = 1, per_page: int = 50) -> tuple[int, list[CategoryOrm]]:
        query = (select(CategoryOrm).offset(
            (page - 1) * per_page).limit(per_page))
        return self.db.execute(query).scalars().all()

    def get(self, category_id: int) -> CategoryOrm | None:
        return self.db.get(CategoryOrm, category_id)

    def get_by_slug(self, slug: str) -> CategoryOrm | None:
        query = select(CategoryOrm).where(CategoryOrm == slug)
        return self.db.execute(query).scalars().first()

    def create(self, *, name: str, slug: str) -> CategoryOrm:
        category = CategoryOrm(name, slug)
        self.db.add(category)
        self.db.flush()
        return category

    def update(self, category:  CategoryOrm, updates: dict) -> CategoryOrm:
        for key, values in updates.items():
            setattr(category, key, values)
        self.db.add(category)
        self.db.flush()
        return category

    def delete(self, category:  CategoryOrm) -> None:
        self.delete(category)
