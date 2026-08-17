import os
from jose import jwt, JWTError
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from . import database, schemas
from . import models
from .config import settings
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer

# tokenUrl must match the actual login route so the Swagger UI lock button works
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict) -> str:
    """Create a JWT access token that expires in ACCESS_TOKEN_EXPIRE_MINUTES minutes."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception: HTTPException) -> schemas.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(user_id=int(user_id))
    except (JWTError, ValueError, TypeError):
        raise credentials_exception
    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_session),
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user