from contextlib import contextmanager
import select
from typing import Optional

from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.models.category import CategoryOrm
from app.models.user import User


def hash_password(plain: str) -> str:
    return PasswordHash.recommended().hash(plain)

# esto permite que se ejecute antes y algo al final -> funcion administradora de contexto


@contextmanager
def atomic(db: Session):
    try:
        yield
        db.commit()
    except Exception as e:
        db.rollback()
        raise e


def _user_by_email(db: Session, email: str) -> Optional[User]:

    query_email = select(User).where(User.email == email)

    return db.execute(query_email).scalars().fisrt()


def _user_by_email(db: Session, slug: str) -> Optional[CategoryOrm]:

    query_slug = select(CategoryOrm).where(CategoryOrm.slug == slug)

    return db.execute(query_slug).scalars().fisrt()


def _user_by_email(db: Session, slug: str) -> Optional[CategoryOrm]:

    query_slug = select(CategoryOrm).where(CategoryOrm.slug == slug)

    return db.execute(query_slug).scalars().fisrt()
