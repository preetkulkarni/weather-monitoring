import os
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from dotenv import load_dotenv
from jose import JWTError, jwt

from ..database import get_db
from ..models import User, log_api_call
from ..schemas import UserCreate, UserResponse, Token

logger = logging.getLogger(__name__)

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("CRITICAL: Secret key not loaded from environment.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12 
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

security = HTTPBearer()

def get_current_user(res: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    Verifies user.
    """
    token = res.credentials 
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return {"user_id": user_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies plain password against hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashes a plain text password.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """
    Generates a JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except JWTError as e:
        logger.error(f"Error encoding JWT: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Could not create access token."
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)) -> Any:
    """
    Registers a new user in the system.
    """
    start_time = time.perf_counter()
    endpoint = "/register"
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        log_api_call(db, endpoint, 409, start_time)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered."
        )

    try:
        hashed_pwd = get_password_hash(user.password)
        new_user = User(email=user.email, hashed_password=hashed_pwd)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        log_api_call(db, endpoint, 201, start_time)

        return new_user

    except Exception as e:
        db.rollback()
        log_api_call(db, endpoint, 500, start_time)
        logger.error(f"Database error during user registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An internal error occurred during registration."
        )


@router.post("/login", response_model=Token)
def login_user(user: UserCreate, db: Session = Depends(get_db)) -> Any:
    """
    Authenticates user and returns a token.
    """
    start_time = time.perf_counter()
    endpoint = "/login"
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        log_api_call(db, endpoint, 401, start_time)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": str(db_user.id)})

    log_api_call(db, endpoint, 200, start_time)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }