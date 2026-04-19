from datetime import datetime
from fastapi import FastAPI, Query, HTTPException, Path, status, Depends
from math import ceil
from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from sqlalchemy import create_engine, Integer, String, Text, DateTime, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, mapped_column, Mapped
from typing import Optional, List, Union, Literal
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")
print("conectado a :", DATABASE_URL)

engine_kwargs = {}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs['connect_args'] = {"check_same_thread": False}


engine = create_engine(DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, class_=Session
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


"""
modelos de post con sql alchamy
"""


class PostORM():
    # decalrar tabla
    __tablename__ = "posts"
    # declarar columnas
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    create_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)


# solo en desarollo ya en porduccion usa migraciones
Base.metadata.create_all(bind=engine)


app = FastAPI(title="mini Blog")

BLOG_POST = [
    {"id": 1, "title": "nala", "content": "Mi fiel nala"},
    {"id": 2, "title": "Odie", "content": "El mas bonito"},
    {"id": 3, "title": "peluche", "content": "Mi primer perro"}

]


class Tag(BaseModel):
    name: str = Field(..., min_length=2, max_length=30,
                      description="Nombre de la ertiqueta")


class Author(BaseModel):
    name: str
    email: EmailStr


class PostBase(BaseModel):
    title: str
    content: str
    # content: Optional[str] = "Esperando contenido descriptivo"
    tags: Optional[List[Tag]] = Field(default_factory=list)
    author: Optional[Author] = None

# * field y validaciones avanzada


class PostCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Titulo del post (minimo 3 Caracteres, maximo 100)",
        examples=["Mi primer post en fastAPI"]
    ),
    content: Optional[str] = Field(
        default="Contenido no disponible",
        min_length=10,
        description="Contenido del post (minimo 10 caracteres)",
        examples=["Este ees un contenido valido porque tiene 10 caracteres"]
    ),
    # [] crea una lista de forma dependiente
    tags: list[Tag] = Field(default_factory=list)
    author: Optional[Author] = None

    # * validacion perzonalizada -> atravez de metodo y se puede reutilizar

    @field_validator("title")
    @classmethod
    def validate_titulo_content(cls, value: str) -> str:
        if "spam" in value.lower():
            raise ValueError("El title no pude contener la palabra: 'spam'")
        return value


# * validaciones sencillas y optionales
class postUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=10)
    content: Optional[str] = None
    """
    o agregarle un valor por defecto   content: Optional[str] = "valor por defecto"
    """


class postPublic(PostBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class Postsummary(BaseModel):
    id: int
    title: str
    # con esto validamos objetos y sin este es solo diccionarios
    model_config = ConfigDict(from_attributes=True)


class PaginatedPost(BaseModel):
    page: int
    per_page: int
    total: int
    total_page: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"]
    direction: Literal["asc", "desc"]
    search: Optional[str] = None
    items: list[postPublic]


@app.get("/")
def home():
    return {'message': "bienvenidos a mini blog"}

# payload estatica a un ednpoint


"""
los query parametres sirven para filtrar y buscar y perzonalizar una peticion
  ordenado limitado etc.

  como quiero traer ese recurso

"""

"""
rewsponse model  se encragzara de hacer que compla con un molde de acuerdo a l,o que vamsos a definir`
"""

# validacion con QueryParameters
"""
el deprecated que se usa para  cuando vamos a modificar una api y dicho paametro ya no vamos a ocupar
"""


@app.get("/posts", response_model=PaginatedPost)
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
    results = select(PostORM)
    total_pages = ceil(total/per_page) if total > 0 else 0

    if query:
        results = results.where(PostORM.title.ilike(f"%{query}%"))
        # return {"payload": results, "query": query}

        total = db.scalar(select(func.count()).select_from(
            results.subquery())) or 0

        current_page = 1 if total_pages == 0 else min(page, total_pages)

        if order_by == "id":
            order_col = PostORM.id
        else:
            order_col = func.lower(PostORM.title)

        results = results, order_by(
            order_col.asc() if direction == "asc" else order_col.desc())

        # results = sorted(
        #     results, key=lambda post: post[order_by], reverse=(direction == "desc"))

    if total_pages == 0:
        items = list[PostORM] = []
    else:
        start = (current_page - 1) * per_page
        items = db.execute(results.limit(
            per_page).offset(start)).scalars().all()

    has_prev = current_page > 1
    has_next = current_page < total_pages

    # items = results[page:offset + limit]
    # for post in BLOG_POST:
    #     if query.lower() in post['title'].lower():
    #         results.append(post)

    # return {"payload": BLOG_POST}

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


"""
path parameters define un recurso ecxato que quermaos forma parte de la url
"""

# ya ccon pydantic
# validacion de path


@app.get("/posts/{post_id}", response_model=Union[postPublic, Postsummary], response_description="Post encontradfo")
def get_post(post_id: int = Path(
    ...,
    ge=1,
    title="ID del Post",
    description="Identifiador entero del post. deber ser mayr a uno",
    example=1

), content: bool = Query(default=True, description="Incluir o no el contenido"), db: Session = Depends(get_db)):

    post_find = select(PostORM).where(PostORM.id == post_id)
    post = db.execute(post_find).scalar_one_or_none()

#    post = db.get(PostORM, post_id)

    if not post:
        raise HTTPException(
            status_code=404, detail="Post no encontrado"
        )

    if content:
        return postPublic.model_validate(post, from_attributes=True)

    return Postsummary.model_validate(post, from_attributes=True)


"""
Metodo Post

"""


@app.post("/posts", response_model=postPublic, response_description="metodo post (ok)", status_code=status.HTTP_201_CREATED)
def create_posts(post: PostCreate, db: Session = Depends(get_db)):
    new_Post = PostORM(title=post.title, content=post.content)

    try:
        db.add(new_Post)
        db.commit()
        db.refresh(new_Post)
        return new_Post
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al crear el post")


#     new_id = (BLOG_POST[-1]["id"]+1) if BLOG_POST else 1
# # model dump transforma  de objeto a diccionario
#     new_post = {"id": new_id,
#                 "title": post.title,
#                 "content": post.content,
#                 "tags": [tag.model_dump() for tag in post.tags],
#                 "author": post.author.model_dump() if post.author else None
#                 }
#     BLOG_POST.append(new_post)
#     return new_post


"""
multiples variables con queryParams

"""


@app.get("/posts/by-tags", response_model=List[postPublic])
def filter_by_tags(
    tags: list[str] = Query(
        ...,
        min_length=2,
        description="una o mas etiquetas. Ejemplo: ?tags=python&tags=fastapi"
    )

):
    tags_lower = [tag.lower() for tag in tags]

    return [
        post for post in BLOG_POST if any(tag["name"].lower() in tags_lower for tag in post.get("tags", []))
    ]


"""
Metodo put

"""


@app.put("/posts/{post_id}", response_model=postPublic)
def update_post(post_id: int, payload: postUpdate, db: Session = Depends(get_db)):

    post = db.get(PostORM, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="No se encontro el post")

    updates = payload.model_dump(exclude_unset=True)

    for key, value in updates.items():
        setattr(post, key, value)

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


"""
metodo delete
"""


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletePost(post_id: int, db: Session = Depends(get_db)):

    post = db.get(PostORM, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="No se encontro el post")

    db.delete(post)
    db.commit()
    
    return 

# *
