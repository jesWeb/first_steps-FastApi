from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Tag(BaseModel):
    name: str = Field(..., min_length=2, max_length=30,
                      description="Nombre de la ertiqueta")
    model_config = ConfigDict(from_attributes=True)


class Author(BaseModel):
    name: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    title: str
    content: str
    # content: Optional[str] = "Esperando contenido descriptivo"
    tags: Optional[List[Tag]] = Field(default_factory=list)
    author: Optional[Author] = None
    model_config = ConfigDict(from_attributes=True)

# * field y validaciones avanzada


class PostCreate(BaseModel):
    title: str = Field(
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

    @field_validator("title")
    @classmethod
    def validate_titulo_content(cls, value: str) -> str:
        if "spam" in value.lower():
            raise ValueError("El title no pude contener la palabra: 'spam'")
        return value


# * validaciones sencillas y optionales
class postUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=10)
    content: Optional[str] = None
    """
    o agregarle un valor por defecto   content: Optional[str] = "valor por defecto"
    """


class postPublic(PostBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class Postsummary(BaseModel):
    id: int
    title: str
    # con esto validamos objetos y sin este es solo diccionarios
    model_config = ConfigDict(from_attributes=True)


class PaginatedPost(BaseModel):
    page: int
    per_page: int
    total: int
    total_page: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"]
    direction: Literal["asc", "desc"]
    search: Optional[str] = None
    items: list[postPublic]
