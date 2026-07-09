
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, PyJWTError
from sqlalchemy.orm import Session

from app.api.v1.auth.repository import UserRepository
from app.core.config import settings
from app.core.db import get_db
from app.models.user import User
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     expire = datetime.now(
#         tz=timezone.utc) + (expires_delta or timedelta(minutes=secrets.ACCES_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     token = jwt.encode(payload=to_encode, key=secrets.JWT_SECRET,
#                        algorithm=secrets.JWT_ALGORITHM)
#     return token


def raise_frobidden():
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos Suficientes",
    )


def invalid_credentials():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales Invalidas",
    )


def decode_token(token: str) -> dict:
    payload = jwt.decode(jwt=token, key=settings.JWT_SECRET,
                         algorithms=[settings.JWT_ALGORITH])
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
        # username: Optional[str] = payload.get("username")

        if not sub :
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

    def evaluation(user: User = Depends(get_current_user)) -> User:
        if order[user.role] < order[min_role]:
            raise raise_frobidden()
        return user

    return evaluation


async def auth2_token(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    repository = UserRepository(db)

    user = repository.get_by_email(form.username)

    if not user or not verify_password(form.password, user.hased_password):
        raise invalid_credentials()

    token = create_access_token(sub=str(user.id))

    return {"access_token": token, "token_type": "bearer"}

require_user = require_role("user")

require_editor = require_role("editor")

require_admin = require_role("admin")
