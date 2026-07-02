from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.api.v1.auth.repository import UserRepository
from app.core.db import get_db
from app.models.user import User
from .schemas import TokenResponse, UserPublic, roleUpdate, userCreate, userLogin
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token, get_current_user, hash_password, verify_password, require_admin, auth2_token

# FAKE_USERS = {
#     "ricardo@example.com": {"email": "ricardo@example.com", "username": "ricardo", "password": "secret123"},
#     "alumno@example.com":  {"email": "alumno@example.com",  "username": "alumno",  "password": "123456"},
# }

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: userCreate, db: Session = Depends(get_db)):
    repository = UserRepository(db)

    if repository.get_by_email(payload.email):
        raise HTTPException(status_code=400, detail="Email ya registrado")
    user = repository.create_user(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name
    )
    db.commit()
    db.refresh(user)
    return UserPublic.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: userLogin, db: Session = Depends(get_db)):
    repository = UserRepository(db)
    user = repository.get_by_email(payload.email)
    if not user or verify_password(payload.password, user.hased_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas")

    token = create_access_token(sub=str(user.id))

    return TokenResponse(access_token=token, user=UserPublic.model_validate(user))


@router.get("/me", response_model=UserPublic)
async def read_me(current: User = Depends(get_current_user)):
    return UserPublic.model_validate(current)


@router.put("/role/{user_id}", response_model=UserPublic)
def set_role(

    user_id: int = Path(..., ge=1),
    payload: roleUpdate = None,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    respository = UserRepository(db)
    user = respository.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    updates = respository.set_role(user, payload.role)

    db.commit()
    db.refresh(user)
    return UserPublic.model_validate(updates)


@router.post("/token")
async def token_endpoint(response=Depends(auth2_token)):

    return response
