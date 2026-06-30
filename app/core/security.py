
from datetime import datetime, timedelta, timezone
import secrets
from typing import Literal, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, PyJWTError
from sqlalchemy import literal
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.db import get_db
from app.models.user import User
from pwdlib import PasswordHash

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
password_hash = PasswordHash.recommended()

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     expire = datetime.now(
#         tz=timezone.utc) + (expires_delta or timedelta(minutes=secrets.ACCES_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     token = jwt.encode(payload=to_encode, key=secrets.JWT_SECRET,
#                        algorithm=secrets.JWT_ALGORITHM)
#     return token


def decode_token(token: str) -> dict:
    payload = jwt.decode(jwt=token, key=secrets.JWT_SECRET,
                         algorithms=[secrets.JWT_ALGORITH])
    return payload


def create_access_token(sub: str, minutes: int | None = None) -> str:
    expire = datetime.now(
        timezone.utc) + timedelta(minutes=minutes or settings.ACCES_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": sub, "exp": expire}, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITH)
    # *btener el usuario


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exec = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = decode_token(token)
        sub: Optional[str] = payload.get("sub")
        username: Optional[str] = payload.get("username")

        if not sub or not username:
            raise credentials_exec

        user_id = int(sub)

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    except InvalidTokenError:
        raise credentials_exec
    except PyJWTError:
        raise credentials_exec

    user = db.get(User, user_id)

    if not user or not user.is_active:
        raise credentials_exec

    return user


def hash_password(plain: str) -> str:
    return password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)


def require_role(min_role: Literal["user", "editor", "admin"]):
    order = {"user": 0, "editor": 1, "admin": 2}

    def evaluation(user:User = Depends(get_current_user))->User:
        if order[user.role] < order[min_role]:
            raise raise_frobidden()
        return user
    
    return evaluation


require_user = require_role("user")

require_editor = require_role("editor")

require_admin = require_role("admin")