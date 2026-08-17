from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_session
from app import schemas
from app.models import User
from app.utils import hash, verify
from app.Oauth2 import create_access_token
from sqlalchemy.exc import IntegrityError


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.Userout)
def register(user_create: schemas.UserCreate, db: Session = Depends(get_session)):
    """
    Register a new user. Passwords are hashed with pbkdf2_sha256 before storage.
    Returns the created user without the password.
    """
    hashed_password = hash(user_create.password)
    new_user = User(
        username=user_create.username,
        email=str(user_create.email),
        password=hashed_password,
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email or username already exists",
        )

    return schemas.Userout(id=new_user.id, email=new_user.email, created_at=new_user.created_at)


@router.post("/login", response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session),
):
    """
    Login with email or username + password.
    Returns a JWT access token valid for ACCESS_TOKEN_EXPIRE_MINUTES minutes.
    """
    username = user_credentials.username
    password = user_credentials.password

    db_user = db.query(User).filter(
        (User.email == username) | (User.username == username)
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not verify(password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(data={"user_id": db_user.id})
    return schemas.Token(access_token=access_token, token_type="bearer")
