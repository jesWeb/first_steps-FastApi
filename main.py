from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Union
app = FastAPI(title="mini Blog")

BLOG_POST = [
    {"id": 1, "title": "nala", "content": "Mi fiel nala"},
    {"id": 2, "title": "Odie", "content": "El mas bonito"},
    {"id": 3, "title": "peluche", "content": "Mi primer perro"}

]


class Tag(BaseModel):
    name: str = Field(..., min_length=2, max_length=30,
                      description="Nombre de la ertiqueta")


class PostBase(BaseModel):
    title: str
    content: Optional[str] = "Esperando contenido descriptivo"
    tags: List[Tag] = []

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
    tags: list[Tag] = []

    # * validacion perzonalizada -> atravez de metodo y se puede reutilizar
    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        if "spam" in value.lower():
            raise ValueError("El titulo no pude contener la palabra: 'spam'")
        return value


# * validaciones sencillas y optionales
class postUpdate(BaseModel):
    title: str
    content: Optional[str] = None
    """
    o agregarle un valor por defecto   content: Optional[str] = "valor por defecto"
    """


class postPublic(PostBase):
    id: int


class Postsummary(BaseModel):
    id: int
    title: str


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


@app.get("/posts", response_model=List[postPublic])
def list_posts(query: str | None = Query(default=None, description="Text para buscar")):

    if query:
        results = [post for post in BLOG_POST if query.lower()
                   in post['title'].lower()]
        # return {"payload": results, "query": query}
        return results

        # for post in BLOG_POST:
        #     if query.lower() in post['title'].lower():
        #         results.append(post)

    # return {"payload": BLOG_POST}

    return BLOG_POST


"""
path parameters define un recurso ecxato que quermaos forma parte de la url
"""

# ya ccon pydantic


@app.get("/posts/{post_id}", response_model=Union[postPublic, Postsummary], response_description="Post encontradfo")
def get_post(post_id: int, content: bool = Query(default=True, description="Incluir o no el contenido")):
    for post in BLOG_POST:
        if post['id'] == post_id:
            if not content:
                return {"id": post['id'], "title": post['title']}
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

    new_post = {"id": new_id,
                "title": post.title, "content": post.content,"tags":[tag.model_dump() for tag in post.tags]}
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
            if "title" in payload:
                post["title"] = payload["title"]
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
