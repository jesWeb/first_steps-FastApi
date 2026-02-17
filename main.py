from fastapi import FastAPI

app = FastAPI(title="mini Blog")

@app.get("/")

def home():
    return {'message':"bienvenidos a mini blog"}
