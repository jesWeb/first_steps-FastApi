from fastapi import FastAPI, Query, Body, HTTPException
from pydantic import BaseModel
app = FastAPI(title="mini Blog")

BLOG_POST = [
    {"id": 1, "title": "nala", "include_content": "Mi primer post con nala"},
    {"id": 2, "title": "nala", "include_content": "Mi primer post con nala"},
    {"id": 3, "title": "nala", "include_content": "Mi primer post con nala"}

]


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class postUpdate(BaseModel):
    title: str
    content: str


@app.get("/")
def home():
    return {'message': "bienvenidos a mini blog"}

# data estatica a un ednpoint


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
        return {"data": results, "query": query}
        # for post in BLOG_POST:
        #     if query.lower() in post['title'].lower():
        #         results.append(post)

    return {"data": BLOG_POST}


"""
path parameters define un recurso ecxato que quermaos forma parte de la url
"""

# ya ccon pydantic


@app.get("/posts/{post_id}")
def get_post(post_id: int, include_content: bool = Query(default=True, description="Incluir o no el contenido")):
    for post in BLOG_POST:
        if post['id'] == post_id:
            if not include_content:
                return {"id": post['id'], "title": post['title']}
            return {"data": post}
    return {"error": "post no encontrado"}


"""
Metodo Post

"""


@app.post("/posts")
def create_posts(post:PostCreate):

    new_id = (BLOG_POST[-1]["id"]+1) if BLOG_POST else 1

    new_post = {"id": new_id,
                "title": post.title, "content": post.content}
    BLOG_POST.append(new_post)
    return {"mesagge": "Post creado", "data": new_post}


"""
Metodo put

"""


@app.put("/posts/{post_id}")
def update_post(post_id: int, data:postUpdate):
    for post in BLOG_POST:
        if post["id"] == post_id:
            payload = data.model_dump(exclude_unset=True)
            if "title" in payload:
                post["title"] = data["title"]
            if "content" in payload:
                post["content"] = data["content"]
            return {"menssage": "Post actualizado", "data": post}

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
