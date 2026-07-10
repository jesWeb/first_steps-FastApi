
import os
from fastapi import FastAPI
from app.core.db import Base, engine
from dotenv import load_dotenv
from app.api.v1.posts.router import router as post_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.uploads.router import router as upload_router
from app.api.v1.tags.router import router as tag_router
from app.api.v1.category.router import router as cate_router
from fastapi.staticfiles import StaticFiles

load_dotenv()
# solo en desarollo ya en porduccion usa migraciones

MEDIA_DIR = "app/media"


def create_app() -> FastAPI:
    app = FastAPI(title="Mini Blog")
    Base.metadata.create_all(bind=engine)  # dev
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(post_router)
    app.include_router(upload_router)
    app.include_router(tag_router)
    app.include_router(cate_router)
    os.makedirs(MEDIA_DIR, exist_ok=True)
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

    return app


app = create_app()

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
"""
path parameters define un recurso ecxato que quermaos forma parte de la url
"""
