from math import ceil
from typing import List, Literal, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import APIRouter, Depends, status, Path, Query, HTTPException
from app.core.db import get_db
from .schemas import (postPublic, PaginatedPost,
                      PostCreate, postUpdate, Postsummary)
from .repository import PostRepository

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=PaginatedPost)
def list_posts(
    text: Optional[str] = Query(
        default=None,
        deprecated=True,
        description="Parametro pobsoleto,usa query o search en su lugar"
    ),
    query: Optional[str] = Query(
        default=None,
        description="Text para buscar",
        alias="search",
        min_length=3,
        max_length=8,
        pattern=r"z[a-zA-Z]+$"
    ),
    # paginacin con queryparasm
    per_page: int = Query(
        10, ge=1, le=50,
        description="Numero de pagina (1-50)"
    ),
    page: int = Query(
        1, ge=1,
        description="Elementos a saltar antes de empezar la lista"
    ),
    order_by: Literal["id", "title"] = Query(
        "id", description="Campo de orden"
    ),
    direction: Literal["asc", "desc"] = Query(
        "asc", description="Direccion de orden "
    ),
    db: Session = Depends(get_db)
):
    repository = PostRepository(db)
    query = query or text

    total, items = repository.search(
        query, order_by, direction, page, per_page
    )

    total_pages = ceil(total/per_page) if total > 0 else 0
    current_page = 1 if total_pages == 0 else min(page, total_pages)

    has_prev = current_page > 1
    has_next = current_page < total_pages

    return PaginatedPost(
        pages=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        direction=direction,
        search=query,
        items=items
    )


@router.get("/by-tags", response_model=List[postPublic])
def filter_by_tags(
    tags: list[str] = Query(
        ...,
        min_length=2,
        description="una o mas etiquetas. Ejemplo: ?tags=python&tags=fastapi"
    ),
    db: Session = Depends(get_db)
):
    repository = PostRepository(db)
    return repository.by_tags(tags)


@router.get("/{post_id}", response_model=Union[postPublic, Postsummary], response_description="Post encontrado")
def get_post(post_id: int = Path(
    ...,
    ge=1,
    title="ID del Post",
    description="Identifiador entero del post. deber ser mayr a uno",
    example=1

), content: bool = Query(default=True, description="Incluir o no el contenido"), db: Session = Depends(get_db)):
    repository = PostRepository(db)
    post = repository.get(post_id)

    if not post:
        raise HTTPException(
            status_code=404, detail="Post no encontrado"
        )

    if content:
        return postPublic.model_validate(post, from_attributes=True)

    return Postsummary.model_validate(post, from_attributes=True)


@router.post("", response_model=postPublic, response_description="metodo post (ok)", status_code=status.HTTP_201_CREATED)
def create_posts(post: PostCreate, db: Session = Depends(get_db)):
    """Author"""

    repository = PostRepository(db)

    try:
        post = repository.create_post(title=post.title, content=post.content, author=(
            post.author.model_dump() if post.author else None), tags=[tag.model_dump() for tag in post.tags]),

        db.commit()
        return post
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="El titulo ya existe,prueba con otro"
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear el post")


@router.put("/{post_id}", response_model=postPublic)
def update_post(post_id: int, payload: postUpdate, db: Session = Depends(get_db)):

    respository = PostRepository(db)
    post = respository.get(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="No se encontro el post")

    try:

        updates = payload.model_dump(exclude_unset=True)
        post = respository.update_post(post, updates)
        db.commit()
        db.refresh(db)
        return post
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="error al actualizar post")


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletePost(post_id: int, db: Session = Depends(get_db)):
    repository = PostRepository(db)
    post = repository.get(post_id)
    try:
        repository.deletePost(post)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error al eliminar al post")
