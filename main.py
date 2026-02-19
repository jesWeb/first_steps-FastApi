from fastapi import FastAPI, Query

app = FastAPI(title="mini Blog")

BLOG_POST = [
    {"id": 1, "title": "nala", "content": "Mi primer post con nala"},
    {"id": 2, "title": "nala", "content": "Mi primer post con nala"},
    {"id": 3, "title": "nala", "content": "Mi primer post con nala"}

]


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


@app.get("/posts/{post_id}")
def get_post(post_id: int, content: bool = Query(default=True, description="Incluir o no el contenido")):
    for post in BLOG_POST:
        if post['id'] == post_id:
            if not content:
                return {"id": post['id'], "title": post['title']}
            return {"data": post}
    return {"error": "post no encontrado"}
