import os
from fastapi import FastAPI, Query, HTTPException, Path
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional, List, Union, Literal
from math import ceil
from sqlalchemy.orm import sessionmaker, Session,DeclarativeBase
from sqlalchemy import create_engine
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")
print("conectado a :", DATABASE_URL)

engine_kwargs = {}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs['connect_args'] = {"check_same_thread": False}


engine = create_engine(DATABASE_URL, echo=True, future=True, autocommit=False)

SessionLocal = sessionmaker(
    bind=engine,autoflush=False,autocommit=False,class_=Session
)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    
    try:
        yield db
    finally:
        db.close()





app = FastAPI(titulo="mini Blog")

BLOG_POST = [
    {"id": 1, "titulo": "nala", "content": "Mi fiel nala"},
    {"id": 2, "titulo": "Odie", "content": "El mas bonito"},
    {"id": 3, "titulo": "peluche", "content": "Mi primer perro"}

]


class Tag(BaseModel):
    name: str = Field(..., min_length=2, max_length=30,
                      description="Nombre de la ertiqueta")


class Author(BaseModel):
    name: str
    email: EmailStr


class PostBase(BaseModel):
    titulo: str
    content: str
    # content: Optional[str] = "Esperando contenido descriptivo"
    tags: Optional[List[Tag]] = Field(default_factory=list)
    author: Optional[Author] = None

# * field y validaciones avanzada


class PostCreate(BaseModel):
    titulo: str = Field(
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

    @field_validator("titulo")
    @classmethod
    def validate_titulo_content(cls, value: str) -> str:
        if "spam" in value.lower():
            raise ValueError("El titulo no pude contener la palabra: 'spam'")
        return value


# * validaciones sencillas y optionales
class postUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=3, max_length=10)
    content: Optional[str] = None
    """
    o agregarle un valor por defecto   content: Optional[str] = "valor por defecto"
    """


class postPublic(PostBase):
    id: int


class Postsummary(BaseModel):
    id: int
    titulo: str


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
    )
):
    results = BLOG_POST
    total_pages = ceil(total/per_page) if total > 0 else 0

    if total_pages == 0:
        current_page = 1
    else:
        current_page = min(page, total_pages)

    if query:
        results = [post for post in results if query.lower()
                   in post['titulo'].lower()]
        # return {"payload": results, "query": query}

        total = len(results)

        results = sorted(
            results, key=lambda post: post[order_by], reverse=(direction == "desc"))

    if total_pages == 0:
        items = []
    else:
        start = (current_page - 1) * per_page
        items = results[start:start + per_page]

    has_prev = current_page > 1
    has_next = current_page < total_pages

    # items = results[page:offset + limit]
    # for post in BLOG_POST:
    #     if query.lower() in post['titulo'].lower():
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

), content: bool = Query(default=True, description="Incluir o no el contenido")):
    for post in BLOG_POST:
        if post['id'] == post_id:
            if not content:
                return {"id": post['id'], "titulo": post['titulo']}
            return post
    return HTTPException(
        status_code=404, detail="Post no encontrado"
    )


"""
Metodo Post

"""


@app.post("/posts", response_model=postPublic, response_description="metodo post (ok)")
def create_posts(post: PostCreate):

    new_id = (BLOG_POST[-1]["id"]+1) if BLOG_POST else 1
# model dump transforma  de objeto a diccionario
    new_post = {"id": new_id,
                "titulo": post.titulo,
                "content": post.content,
                "tags": [tag.model_dump() for tag in post.tags],
                "author": post.author.model_dump() if post.author else None
                }
    BLOG_POST.append(new_post)
    return new_post


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
def update_post(post_id: int, payload: postUpdate):
    for post in BLOG_POST:
        if post["id"] == post_id:
            payload = payload.model_dump(exclude_unset=True)
            if "titulo" in payload:
                post["titulo"] = payload["titulo"]
            if "content" in payload:
                post["content"] = payload["content"]
            return post

    raise HTTPException(status_code=404, detail="No se encontro el post")


"""
metodo delete 
"""


@app.delete("/posts/{post_id}", status_code=204)
def deletePost(post_id: int):
    for index, post in enumerate(BLOG_POST):
        BLOG_POST.pop(index)
        return
    raise HTTPException(status_code=404, detail="Post no encontrado")

# *
