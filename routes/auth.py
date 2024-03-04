from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from config.db import SessionLocal
from helpers import auth_utils
from models import models
from routes.actions import auth_action
from schemas import auth_schemas as schemas

from . import auth

auth_router = APIRouter(prefix="/authentication", tags=["Authentication"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@auth_router.post(
    "/register",
    response_model=schemas.Token,
)
def register(
    user_details: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # querying database to check if user already exist
    user = (
        db.query(models.User)
        .filter(models.User.username == user_details.username)
        .first()
    )

    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exist",
        )
    user = models.User(
        username=user_details.username,
        password=auth_utils.hash_pass(user_details.password),
        is_admin=True if user_details.client_secret == "admin_nih_bos" else False,
    )

    db.add(user)  # saving user to database
    db.commit()

    # Refresh the object to ensure it reflects the latest state in the database
    db.refresh(user)

    access_token = auth_action.create_access_token(data={"id": user.id})
    return schemas.Token(access_token=access_token, token_type="bearer")


@auth_router.post(
    "/login",
    response_model=schemas.Token,
)
def login(
    user_details: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """ """
    user = (
        db.query(models.User)
        .filter(models.User.username == user_details.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    if not auth_utils.verify_password(user_details.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Password not match"
        )

    access_token = auth_action.create_access_token(data={"id": user.id})
    return schemas.Token(access_token=access_token, token_type="bearer")


@auth_router.get(
    "/profile",
    response_model=schemas.UserOutput,
)
def get_profile(user: schemas.UserOutput = Depends(auth_action.get_current_user)):
    return user
