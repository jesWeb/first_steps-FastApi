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


@app.get("/posts")
def list_posts(query: str | None = Query(default=None, description="Text para buscar")):

    if query:
        results = [post for post in BLOG_POST if query.lower() in post['title'].lower()]
        return {"data": results, "query": query}
        # for post in BLOG_POST:
        #     if query.lower() in post['title'].lower():
        #         results.append(post)

    return {"data": BLOG_POST}

