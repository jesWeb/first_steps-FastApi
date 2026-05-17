"""FORMA DE IMPORTAR los archivos o completos"""
from .author import AuthorORM
from .tag import TagOrm
from .post import PostORM, post_tags

# importar todo
__all__ = ["AuthorORM", "TagORM", "PostORM", "post_tags"]
