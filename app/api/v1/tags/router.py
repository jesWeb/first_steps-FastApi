
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.tags.repository import tagRepository
from app.api.v1.tags.schemas import TagCreate, TagPublic, TagUpdate
from app.core.db import get_db
from app.core.security import get_current_user, oauth2_scheme, require_user, require_admin, require_editor
from app.models.user import User


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
def create_Tag(tag: TagCreate, db: Session = Depends(get_db), _editor: User = Depends(require_editor)):
    repository = tagRepository(db)
    try:

        tag_created = repository.create_tag(name=tag.name)
        db.commit()
        db.refresh(tag_created)
        return tag_created

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="error al crear el tag")


@router.put("/{tag_id}", response_model=TagPublic, response_description="Tag actualizado")
def update_tag(
    tag_id: int,
    payload: TagUpdate,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_editor)
):
    repository = tagRepository(db)
    tag_obj = repository.update(tag_id, name=payload.name)

    if not tag_obj:
        raise HTTPException(status_code=404, detail="Tag no encontrado")

    try:
        db.commit()
        return TagPublic.model_validate(tag_obj)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="error al actualizar el tag")


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    repository = tagRepository(db)
    tag = repository.delete(tag_id)

    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")

    try:
        db.commit()
        return None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error al eliminar el tag")


@router.get("/secure")
def secure_endpoint(token: str = Depends(oauth2_scheme)):
    return {"message": "Acceso con token", "token_recibido": token}


@router.get("/popular/top")
def get_popular(
    db: Session = Depends(get_db),
        _user: User = Depends(require_user)):

    repository = tagRepository(db)
    popular = repository.most_popular()

    if not popular:
        raise HTTPException(
            status_code=404, detail="No hay Tag encontrado y no es popular")

    return popular
