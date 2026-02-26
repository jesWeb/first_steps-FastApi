from fastapi import FastAPI, Query, Body, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
app = FastAPI(title="mini Blog")

BLOG_POST = [
    {"id": 1, "title": "nala", "content": "Mi fiel nala"},
    {"id": 2, "title": "Odie", "content": "El mas bonito"},
    {"id": 3, "title": "peluche", "content": "Mi primer perro"}

]


class PostBase(BaseModel):
    title: str
    content: Optional[str] = "Esperando contenido descriptivo"

# * field y validaciones avanzadas


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
    )


# * validaciones sencillas y optionales
class postUpdate(BaseModel):
    title: str
    content: Optional[str] = None
    """
    o agregarle un valor por defecto   content: Optional[str] = "valor por defecto"
    """


@app.get("/")
def home():
    return {'message': "bienvenidos a mini blog"}

# payload estatica a un ednpoint


"""
los query parametres sirven para filtrar y buscar y perzonalizar una peticion 
  ordenado limitado etc.
  
  como quiero traer ese recurso
   
"""


@app.get("/posts")
def list_posts(query: str | None = Query(default=None, description="Text para buscar")):

    if query:
        results = [post for post in BLOG_POST if query.lower()
                   in post['title'].lower()]
        return {"payload": results, "query": query}
        # for post in BLOG_POST:
        #     if query.lower() in post['title'].lower():
        #         results.append(post)

    return {"payload": BLOG_POST}


"""
path parameters define un recurso ecxato que quermaos forma parte de la url
"""

# ya ccon pydantic


@app.get("/posts/{post_id}")
def get_post(post_id: int, content: bool = Query(default=True, description="Incluir o no el contenido")):
    for post in BLOG_POST:
        if post['id'] == post_id:
            if not content:
                return {"id": post['id'], "title": post['title']}
            return {"payload": post}
    return {"error": "post no encontrado"}


"""
Metodo Post

"""


@app.post("/posts")
def create_posts(post: PostCreate):

    new_id = (BLOG_POST[-1]["id"]+1) if BLOG_POST else 1

    new_post = {"id": new_id,
                "title": post.title, "content": post.content}
    BLOG_POST.append(new_post)
    return {"mesagge": "Post creado", "payload": new_post}


"""
Metodo put

"""


@app.put("/posts/{post_id}")
def update_post(post_id: int, payload: postUpdate):
    for post in BLOG_POST:
        if post["id"] == post_id:
            payload = payload.model_dump(exclude_unset=True)
            if "title" in payload:
                post["title"] = payload["title"]
            if "content" in payload:
                post["content"] = payload["content"]
            return {"menssage": "Post actualizado", "payload": post}

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
