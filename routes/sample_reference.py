from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import extract
from sqlalchemy.orm import Session

from config.db import SessionLocal
from helpers.utils import add_years_and_months
from models import models
from reports.pdf_generator import generate_destroy_report
from routes import actions
from routes.actions import sample
from routes.actions.sample import create_sample
from schemas import schemas

reference_router = APIRouter(prefix="/reference", tags=["reference"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@reference_router.post(
    "/",
    response_model=List[schemas.SampleReferenced],
    description="Get all reference sample is stored",
)
def create_new_sample_referenced(
    sample: schemas.SampleRetainedCreate, db: Session = Depends(get_db)
):
    """
    Create a new reference sample.

    :param sample: Request body containing details of the new sample
    :param db: Database session dependency
    :return: Details of the created sample
    """
    new_sample = create_sample(db, sample=sample, SampleModel=models.SampleReferenced)
    return [new_sample]


@reference_router.get(
    "/",
    response_model=List[schemas.SampleProductJoin],
    description="Get all reference sample",
)
def get_referenced_samples_for_product(
    id: str = "", skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Retrieve reference samples associated with a specific sample, or all reference samples if product_code isn't specified.


    :param db: Database session dependency
    :return: List of reference samples for the specified sample
    """
    # Query the database to retrieve reference samples for the specified sample
    if id:
        samples = sample.get_sample_by_id(db, id, models.SampleReferenced)
    else:
        samples = sample.get_all_sample(db, skip, limit, models.SampleReferenced)

    samples = [
        {
            "id": sample.id,
            "product_code": sample.product_code,
            "batch_number": sample.batch_number,
            "manufacturing_date": sample.manufacturing_date,
            "expiration_date": sample.expiration_date,
            "destroy_date": sample.destroy_date,
            "rack_id": sample.rack_id,
            "product_name": sample.product.product_name,
            "shelf_life": sample.product.shelf_life,
        }
        for sample in samples
    ]

    return samples


@reference_router.put(
    "/{id}",
    response_model=schemas.SampleReferenced,
    description="Update a reference sample by ID",
)
def update_retained_sample(
    id: str, sample: schemas.SampleReferenced, db: Session = Depends(get_db)
):
    """
    Update an existing reference sample by ID.

    :param id: ID of the reference sample to update
    :param sample: Request body containing updated details of the reference sample
    :param db: Database session dependency
    :return: Updated details of the reference sample
    """
    # Retrieve the reference sample from the database
    existing_sample = (
        db.query(models.SampleReferenced)
        .filter(models.SampleReferenced.id == id)
        .first()
    )
    if existing_sample is None:
        raise HTTPException(status_code=404, detail="Reference sample not found")

    # Update the attributes of the existing sample with the new data
    for key, value in sample.model_dump().items():
        setattr(existing_sample, key, value)

    # Commit the transaction to save the changes
    db.commit()

    # Return the updated reference sample
    return existing_sample


@reference_router.delete(
    "/{id}",
    response_model=schemas.SampleReferenced,
    description="Delete a reference sample by ID",
)
def delete_retained_sample(id: str, db: Session = Depends(get_db)):
    """
    Delete an existing reference sample by ID.

    :param id: ID of the reference sample to delete
    :param db: Database session dependency
    :return: Details of the deleted reference sample
    """
    # Retrieve the reference sample from the database
    sample_to_delete = (
        db.query(models.SampleReferenced)
        .join(models.Product)
        .filter(models.SampleReferenced.id == id)
        .first()
    )
    if sample_to_delete is None:
        raise HTTPException(status_code=404, detail="Reference sample not found")

    # Delete the reference sample from the database
    db.delete(sample_to_delete)
    db.commit()

    # Return the details of the deleted reference sample
    return sample_to_delete


@reference_router.get(
    "/manufacturing",
    response_model=List[schemas.SampleRetainedBase],
    description="Get a sample with a specified manufacturing date",
)
def get_manufacturing_sample(
    db: Session = Depends(get_db), date: date = Query(default=date.today())
):
    sample = db.query(models.SampleReferenced).where(
        models.SampleReferenced.manufacturing_date == date
    )
    if sample is None:
        raise HTTPException(status_code=404, detail="No sample found")

    return sample


@reference_router.get(
    "/expired",
    response_model=List[schemas.SampleRetainedBase],
    description="Get a sample with a specified expired date",
)
def get_expired_sample(
    db: Session = Depends(get_db), date: date = Query(default=date.today())
):
    sample = db.query(models.SampleReferenced).where(
        models.SampleReferenced.expiration_date == date
    )
    if sample is None:
        raise HTTPException(status_code=404, detail="No sample found")

    return sample


@reference_router.get(
    "/destroy",
    response_model=List[schemas.SampleProductJoin],
    description="Get a sample with a specified destroy date",
)
def get_destroy_sample(month: int, year: int, db: Session = Depends(get_db)):
    samples = (
        db.query(models.SampleReferenced)
        .filter(extract("year", models.SampleReferenced.destroy_date) == year)
        .filter(extract("month", models.SampleReferenced.destroy_date) == month)
    )

    if samples is None:
        raise HTTPException(status_code=404, detail="No sample found")

    reference_samples = [
        {
            "id": sample.id,
            "product_code": sample.product_code,
            "batch_number": sample.batch_number,
            "manufacturing_date": sample.manufacturing_date,
            "expiration_date": sample.expiration_date,
            "destroy_date": sample.destroy_date,
            "rack_id": sample.rack_id,
            "product_name": sample.product.product_name,
            "shelf_life": sample.product.shelf_life,
        }
        for sample in samples
    ]

    return reference_samples


@reference_router.get(
    "/generate-destroy-report", description="Generate destroy reports"
)
def generate_destroy_reports(month: int, year: int, db: Session = Depends(get_db)):
    # Retrieve details for each sample
    samples = (
        db.query(models.SampleReferenced)
        .filter(extract("year", models.SampleReferenced.destroy_date) == year)
        .filter(extract("month", models.SampleReferenced.destroy_date) == month)
    )
    report_date = date(year, month, 1)
    if samples is None:
        raise HTTPException(status_code=404, detail="No sample found")

    sample_referenced = [
        schemas.SampleProductJoin(
            id=sample.id,
            product_code=sample.product_code,
            product_name=sample.product.product_name,
            shelf_life=sample.product.shelf_life,
            batch_number=sample.batch_number,
            manufacturing_date=sample.manufacturing_date,
            expiration_date=sample.expiration_date,
            destroy_date=sample.destroy_date,
            rack_id=sample.rack_id,
        )
        for sample in samples
    ]

    pdf, file_path = generate_destroy_report(
        samples=sample_referenced, date=report_date
    )
    headers = {
        "Content-Disposition": f"attachment; filename=reference-sample_{file_path}"
    }

    return Response(
        content=bytes(pdf.output()), media_type="application/pdf", headers=headers
    )
