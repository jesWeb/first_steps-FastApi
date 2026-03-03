from fastapi import FastAPI, Query, HTTPException, Path
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional, List, Union
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


@app.get("/posts", response_model=List[postPublic])
def list_posts(query:
               Optional[str] = Query(
                   default=None,
                   description="Text para buscar",
                   alias="search",
                   min_length=3,
                   max_length=8,
                   pattern=r"z[a-zA-Z]+$"
               )):

    if query:
        results = [post for post in BLOG_POST if query.lower()
                   in post['titulo'].lower()]
        # return {"payload": results, "query": query}
        return results

        # for post in BLOG_POST:
        #     if query.lower() in post['titulo'].lower():
        #         results.append(post)

    # return {"payload": BLOG_POST}

    return BLOG_POST


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
