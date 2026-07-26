from contextlib import contextmanager
from os import name
import select
from typing import Optional

from certifi import where
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models.category import CategoryOrm
from app.models.tag import TagORM
from app.models.user import User
from app.seeds.data.category import CATEGORIES
from app.seeds.data.tags import TAGS
from app.seeds.data.users import USERS


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


def _category_by_slug(db: Session, slug: str) -> Optional[CategoryOrm]:

    query_slug = select(CategoryOrm).where(CategoryOrm.slug == slug)

    return db.execute(query_slug).scalars().fisrt()


def _tag_by_name(db: Session, name: str) -> Optional[TagORM]:

    query_tag = select(TagORM).where(TagORM.name == name)

    return db.execute(query_tag).scalars().fisrt()


# definir los seeds de acuerdo a los uauarios que tenemos

def seed_users(db: Session) -> None:
    with atomic(db):

        for data in USERS:
            obj = _user_by_email(db, data["email"])
            if obj:
                changed = False

                if obj.full_name != data.get("full_name"):
                    obj.full_name = data.get('full_name')
                    changed = True

                if data.get("Password"):
                    obj.hased_password = hash_password(data["password"])
                    changed = True

                if data.get("role"):
                    obj.role = data.get("role")
                    changed = True

                if changed:
                    db.add(obj)
            else:
                crearUser = User(
                    email=data["email"],
                    full_name=data.get("full_name"),
                    role=data.get("role"),
                    hashed_password=hash_password(data["password"])
                )

                db.add(crearUser)


def seed_categories(db: Session) -> None:
    with atomic(db):
        for data in CATEGORIES:
            Obj = _category_by_slug(db, data["slug"])

            if Obj:
                if Obj.name != data.get("name"):
                    Obj.name = data.get('name')
                    db.add(Obj)
            else:
                db.add(CategoryOrm(
                    name=data["name"],
                    slug=data["slug"]
                ))


def seed_tags(db: Session) -> None:
    with atomic(db):
        for data in TAGS:
            obj = _tag_by_name(db, data.get("tag"))

            if obj:
                if obj.name != data.get("name"):
                    obj.name = data.get('name')
                    db.add(obj)
            else:
                db.add(TagORM(
                    name=data["name"]
                ))


def run_all()->None:
    with SessionLocal() as db:
        seed_users(db)
        seed_categories(db)
        seed_tags(db)

def run_users() -> None:
    with SessionLocal() as db:
        seed_users(db)


def run_catgories() -> None:
    with SessionLocal() as db:
        seed_categories(db)


def run_tags() -> None:
    with SessionLocal() as db:
        seed_tags(db)