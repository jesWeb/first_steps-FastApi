
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.tags.repository import tagRepository
from app.api.v1.tags.schemas import TagCreate, TagPublic
from app.core.db import get_db
from app.core.security import get_current_user


router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=dict)
def list_tags(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    order_by: str = Query("id", pattern="^(id|name)$"),
    direction: str = Query("asc", pattern="^(asc|desc)$"),
    search: str | None = Query(None),
    db: Session = Depends(get_db)
):
    repository = tagRepository(db)

    return repository.listar_Tags(
        search=search,
        order_by=order_by,
        page=page,
        per_page=per_page,
        direction=direction,
    )


@router.post("", response_model=TagPublic, response_description="Post CReado", status_code=status.HTTP_201_CREATED)
def create_Tag(tag: TagCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    repository = tagRepository(db)
    try:
        tag_created = repository.create_tag(name=tag.name)
        db.commit()
        db.refresh(tag_created)
        return tag_created

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="error al crear el tag")
