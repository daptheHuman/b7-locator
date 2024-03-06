from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.db import SessionLocal
from models import models
from routes.actions import auth_action, user_action
from schemas import auth_schemas, user_schemas

users_router = APIRouter(
    prefix="/users", tags=["Users"], dependencies=[Depends(auth_action.is_admin)]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@users_router.get(
    "/",
    response_model=List[auth_schemas.UserOutput],
    dependencies=[Depends(auth_action.is_admin)],
)
def get_all_user(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@users_router.put("/{user_id}", response_model=auth_schemas.UserOutput)
def update_user(
    user_id: int, updated_user: user_schemas.UserUpdate, db: Session = Depends(get_db)
):
    return user_action.update_user(db, user_id, updated_user)


@users_router.delete(
    "/{user_id}",
)
def get_racks_count(user_id: int, db: Session = Depends(get_db)):
    return user_action.delete_user(db, user_id)
