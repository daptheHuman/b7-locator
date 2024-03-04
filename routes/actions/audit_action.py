from typing import List

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models import models
from schemas import audit_schemas


def get_log(
    db: Session,
    query: List[str],
    skip: int,
    limit: int,
) -> List[audit_schemas.AuditOutput]:
    if query:
        filter_condition = or_(
            models.Audit.headers.like(f"%{q}%")
            | models.Audit.request.like(f"%{q}%")
            | models.Audit.timestamp.like(f"%{q}%")
            for q in query
        )
        log = (
            db.query(models.Audit)
            .filter(filter_condition)
            .offset(skip)
            .limit(limit)
            .all()
        )
    else:
        log = db.query(models.Audit).offset(skip).limit(limit).all()

    return log


def clear_all_log(
    db: Session,
) -> List[audit_schemas.AuditOutput]:
    try:
        # Query logs to be cleared
        logs_to_clear = db.query(models.Audit).delete()

        # Return the list of deleted logs
        return logs_to_clear
    except SQLAlchemyError as e:
        # Handle any database errors
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to clear logs")
