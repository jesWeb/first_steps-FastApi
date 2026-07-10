from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.auth import repository
from app.core.db import get_db
from app.api.v1.category.repository import CategoryRepository
from app.api.v1.category.schemas import  CategoryUpdate, categoryCreate, CategoryPublic

router = APIRouter(prefix="/categories", tags=["categories"])

# tarea -> repository listado y los toptales listo y el router


@router.get("", response_model=list[CategoryPublic])
def list_categories(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    repository = CategoryRepository(db)
    return repository.list_many(skip=skip, limit=limit)


@router.post("", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED)
def create_category(data: categoryCreate, db: Session = Depends(get_db)):
    repository = CategoryRepository(db)
    exist = repository.get_by_slug(data.slug)
    if exist:
        raise HTTPException(status_code=400, detail="slug en uso")

    categori = repository.create(name=data.name, slug=data.slug)
    db.commit()
    db.refresh(categori)
    return categori


@router.get("/{category_id}", response_model=CategoryPublic)
def get_category(category_id: int, db: Session = Depends(get_db)):
    repository = CategoryRepository(db)
    catefoty = repository.get(category_id)
    if not catefoty:
        raise HTTPException(status_code=40, detail="Categoria no encontrada")
    return catefoty


@router.put("/{category_id}", response_model=CategoryPublic)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    repository = CategoryRepository(db)
    catefoty = repository.get(category_id)

    if not catefoty:
        raise HTTPException(status_code=40, detail="Categoria no encontrada")

    update = repository.update(catefoty, data.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(update)
    return update


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    repository = CategoryRepository(db)
    catefoty = repository.get(category_id)

    if not catefoty:
        raise HTTPException(status_code=40, detail="Categoria no encontrada")

    delete = repository.delete(catefoty)
    db.commit(delete)
    return None