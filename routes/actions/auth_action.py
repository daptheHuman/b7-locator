from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config.db import SessionLocal
from models import models
from schemas import auth_schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", scheme_name="")

SECRET_KEY = "f816c671db0b6bc5321346bfe247b7671337660a2a1f3def825d11a24fd0f657"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"expire": expire.strftime("%Y-%m-%d %H:%M:%S")})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)

    return encoded_jwt


def verify_token_access(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

        id: str = payload.get("id")

        if id is None:
            raise credentials_exception
        token_data = auth_schemas.DataToken(id=id)
    except JWTError as e:
        raise credentials_exception

    return token_data


security = HTTPBearer()


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> auth_schemas.UserOutput:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not Validate Credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials

    token = verify_token_access(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()
    request.state.username = user.username

    return user


def is_admin(user: auth_schemas.UserOutput = Depends(get_current_user)) -> bool:
    if not user.is_admin:
        credentials_exception = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only",
        )
        raise credentials_exception
    return user.is_admin
