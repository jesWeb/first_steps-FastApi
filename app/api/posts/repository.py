from app.core import db
from app.models import PostORM, AuthorORM
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional

"""Este se encarga de las consultas los repository"""

class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, post_id: int) -> Optional[PostORM]:

        post_find = select(PostORM).where(PostORM.id == post_id)
        return self.db.execute(post_find).scalar_one_or_none()
