# nos ayuda haceer las consultas a la bases de datos
# recuerda que el self es para  guardarlo como una variable interna
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.tags.schemas import TagPublic
from app.models.tag import TagORM
from app.services.pagination import paginate_query


class tagRepository:
    # iniciar la conexion a db
    def __init__(self, db: Session):
        self.db = db

    def create_tag(self, name: str):

        normalize = name.strip().lower()

        tag_obj = self.db.execute(
            select(TagORM).where(func.lower(TagORM.name) == normalize)
        ).scalar_one_or_none()

        if tag_obj:
            return tag_obj

        tag_obj = TagORM(name=name)
        self.db.add(tag_obj)
        self.db.flush()
        return tag_obj

    def listar_Tags(self,
                    search: Optional[str],
                    order_by: str = "id",
                    direction: str = "asc",
                    page: int = 1,
                    per_page: int = 10):
        query = select(TagORM)

        if search:
            query = query.where(func.lower(
                TagORM.name
            ).ilike(f"%{search.lower()}%"))

            allowed_order = {
                "id": TagORM.id,
                "name": func.lower(TagORM.name)
            }
            # inyectar servicio de paginacion

            result = paginate_query(
                db=self.db,
                model=TagORM,
                base_query=query,
                page=page,
                per_page=per_page,
                orde_by=order_by,
                direction=direction,
                allowed_order=allowed_order
            )
            # evitamos el error de python de autenticacon de informacion
            result["items"] = [TagPublic.model_validate(
                item) for item in result["items"]]

        return result
