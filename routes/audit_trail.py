from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.db import SessionLocal
from models import models
from routes.actions import audit_action, auth_action
from schemas import audit_schemas, schemas

audit_router = APIRouter(prefix="/audit", tags=["Audit"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@audit_router.get(
    "/",
    response_model=List[audit_schemas.AuditOutput],
    description="Get all reference sample",
    dependencies=[Depends(auth_action.is_admin)],
)
def get_audit_log(
    query: str = "", skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Retrieve all log with admin role

    :return: List of reference samples for the specified sample
    """
    # Query the database to retrieve reference samples for the specified sample
    log = audit_action.get_log(db, query, skip, limit)
    return log


@audit_router.delete(
    "/",
    response_model=schemas.Sample,
    description="Clear log",
    dependencies=[Depends(auth_action.is_admin)],
)
def clear_all_log(db: Session = Depends(get_db)):
    """
    Clear all log

    :param db: Database session dependency
    :return: Details of the deleted reference sample
    """
    deleted_sample = audit_action.delete_sample(
        db, id, SampleModel=models.SampleReferenced
    )

    # Return the details of the deleted reference sample
    return deleted_sample
