from fastapi import FastAPI
from app.core.db import Base, engine
from dotenv import load_dotenv
from app.api.v1.posts.router import router as post_router
from app.api.v1.auth.router import router as auth_router

load_dotenv()
# solo en desarollo ya en porduccion usa migraciones

def create_app()->FastAPI:
    app = FastAPI(title="mini Blog")
    Base.metadata.create_all(bind=engine)
    app.include_router(auth_router,prefix="/api/v1")
    app.include_router(post_router)
    
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
