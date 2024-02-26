from typing import List

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from config.db import SessionLocal
from models import models
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
    response_model=List[schemas.Sample],
    description="Get all reference sample is stored",
)
def create_new_sample_referenced(
    sample: schemas.SampleCreate, db: Session = Depends(get_db)
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
        schemas.SampleProductJoin(
            id=sample.id,
            product_code=sample.product_code,
            batch_number=sample.batch_number,
            manufacturing_date=sample.manufacturing_date,
            expiration_date=sample.expiration_date,
            destroy_date=sample.destroy_date,
            rack_id=sample.rack_id if sample.rack_id else "",
            product_name=sample.product.product_name,
            shelf_life=sample.product.shelf_life,
        )
        for sample in samples
    ]

    return samples


@reference_router.put(
    "/{id}",
    response_model=schemas.Sample,
    description="Update a reference sample by ID",
)
def update_retained_sample(
    id: str, updated_sample: schemas.Sample, db: Session = Depends(get_db)
):
    """
    Update an existing reference sample by ID.

    :param id: ID of the reference sample to update
    :param sample: Request body containing updated details of the reference sample
    :param db: Database session dependency
    :return: Updated details of the reference sample
    """
    updated_sample = sample.update_sample(
        db, id, updated_sample, SampleModel=models.SampleReferenced
    )

    # Return the updated reference sample
    return updated_sample


@reference_router.delete(
    "/{id}",
    response_model=schemas.Sample,
    description="Delete a reference sample by ID",
)
def delete_retained_sample(id: str, db: Session = Depends(get_db)):
    """
    Delete an existing reference sample by ID.

    :param id: ID of the reference sample to delete
    :param db: Database session dependency
    :return: Details of the deleted reference sample
    """
    deleted_sample = sample.delete_sample(db, id, SampleModel=models.SampleReferenced)

    # Return the details of the deleted reference sample
    return deleted_sample


@reference_router.get(
    "/destroy",
    response_model=List[schemas.SampleProductJoin],
    description="Get a sample with a specified destroy date",
)
def get_destroy_sample(month: int, year: int, db: Session = Depends(get_db)):
    destroy_samples = sample.get_destroy_by_month_year(
        db, month, year, SampleModel=models.SampleReferenced
    )
    return destroy_samples


@reference_router.post(
    "/generate-destroy-report", description="Generate destroy reports"
)
def generate_destroy_reports(
    month: int,
    year: int,
    package_weight: List[schemas.DestroyPackageAndWeight],
    db: Session = Depends(get_db),
):
    pdf, headers = sample.create_destroy_reports(
        db, month, year, package_weight, models.SampleReferenced
    )

    return Response(
        content=bytes(pdf.output()), media_type="application/pdf", headers=headers
    )
