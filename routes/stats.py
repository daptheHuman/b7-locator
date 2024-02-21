from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.db import SessionLocal
from models import models

stats_router = APIRouter(prefix="/stats", tags=["stats"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@stats_router.get("/products/count", response_model=int)
def get_products_count(db: Session = Depends(get_db)):
    count_result = db.query(models.Product).count()
    return count_result


@stats_router.get("/racks/count", response_model=int)
def get_racks_count(db: Session = Depends(get_db)):
    count_result = db.query(models.Rack).count()
    return count_result


@stats_router.get("/retained_samples/count", response_model=int)
def get_retained_count(db: Session = Depends(get_db)):
    count_result = db.query(models.SampleRetained).count()
    return count_result


@stats_router.get("/reference_samples/count", response_model=int)
def get_reference_count(db: Session = Depends(get_db)):
    count_result = db.query(models.SampleReferenced).count()
    return {"total": count_result}
