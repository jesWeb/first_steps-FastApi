"""FORMA DE IMPORTAR los archivos o completos"""
from .author import AuthorORM
from .post import PostORM, post_tags
from .tag import TagOrm

__all__ = ["AuthorORM", "TagOrm", "PostORM", "post_tags"]