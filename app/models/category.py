
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class CategoryOrm(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True, index=True)

    #*Relacioness DB

    #backpopultae sirve para conocer la forma en que vamos ha acceder a el atravex del nombre -> o bien como ba acceder posts a esta categoria 

    #passive_deletes -> cuando se elimina la categoria por ejemplo slqchemy evita toda la consulta select de todoslos objetos secundarios  osea elimina solo los secundarios que esten registrados y si esta en false  al eliminar el post y eliminar el principal pero deja los elementios secundarios 
    
    posts = relationship("PostORM",back_populates="category",cascade="all,delete",passive_deletes=True)