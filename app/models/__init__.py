"""FORMA DE IMPORTAR los archivos o completos"""
from .tag import TagORM
from .post import PostORM, post_tags
from .user import User
from .category import CategoryOrm

__all__ = ["TagORM", "PostORM", "post_tags", "User","CategoryOrm"]
