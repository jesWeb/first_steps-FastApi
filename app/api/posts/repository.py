from math import ceil

from app.core import db
from app.models import PostORM, AuthorORM
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from typing import Optional

"""Este se encarga de las consultas los repository"""


class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, post_id: int) -> Optional[PostORM]:

        post_find = select(PostORM).where(PostORM.id == post_id)
        return self.db.execute(post_find).scalar_one_or_none()

    def search(self, query: Optional[str], order_by: str, direction: str, page: int, per_page: int) -> tuple[int, list[PostORM]]:

        results = select(PostORM)

        if query:
            results = results.where(PostORM.title.ilike(f"%{query}%"))
            # return {"payload": results, "query": query}

            total = db.scalar(select(func.count()).select_from(
                results.subquery())) or 0

            if total == 0:
                return 0, []

            current_page = min(page, max(ceil(total/per_page)))

            order_col = PostORM.id if order_by == "id" else func.lower(
                PostORM.title)

            results = results, order_by(
                order_col.asc() if direction == "asc" else order_col.desc())

            start = (current_page - 1) * per_page
            items = self.db.execute(results.limit(
                per_page).offset(start)).scalars().all()
            
            return total, items
