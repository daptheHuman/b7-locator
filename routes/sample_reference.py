from typing import List

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from config.db import SessionLocal
from models import models
from routes.actions import auth_action, sample_action
from routes.actions.sample_action import create_sample
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
    id: str | None = None,
    skip: int | None = None,
    limit: int | None = None,
    db: Session = Depends(get_db),
):
    """
    Retrieve reference samples associated with a specific sample, or all reference samples if product_code isn't specified.


    :param db: Database session dependency
    :return: List of reference samples for the specified sample
    """
    # Query the database to retrieve reference samples for the specified sample
    if id:
        samples = sample_action.get_sample_by_id(db, id, models.SampleReferenced)
    else:
        samples = sample_action.get_all_sample(db, skip, limit, models.SampleReferenced)

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
            package=sample.product.package,
            product_type=sample.product.product_type,
            shelf_life=sample.product.shelf_life,
        )
        for sample in samples
    ]

    return samples


@reference_router.put(
    "/{id}",
    response_model=schemas.Sample,
    description="Update a reference sample by ID",
    dependencies=[Depends(auth_action.is_admin)],
)
def update_referenced_sample(
    id: str, updated_sample: schemas.Sample, db: Session = Depends(get_db)
):
    """
    Update an existing reference sample by ID.

    :param id: ID of the reference sample to update
    :param sample: Request body containing updated details of the reference sample
    :param db: Database session dependency
    :return: Updated details of the reference sample
    """
    updated_sample = sample_action.update_sample(
        db, id, updated_sample, SampleModel=models.SampleReferenced
    )

    # Return the updated reference sample
    return updated_sample


@reference_router.delete(
    "/{id}",
    response_model=schemas.Sample,
    description="Delete a reference sample by ID",
    dependencies=[Depends(auth_action.is_admin)],
)
def delete_retained_sample(id: str, db: Session = Depends(get_db)):
    """
    Delete an existing reference sample by ID.

    :param id: ID of the reference sample to delete
    :param db: Database session dependency
    :return: Details of the deleted reference sample
    """
    deleted_sample = sample_action.delete_sample(
        db, id, SampleModel=models.SampleReferenced
    )

    # Return the details of the deleted reference sample
    return deleted_sample


@reference_router.get(
    "/destroy",
    response_model=List[schemas.SampleProductJoin],
    description="Get a sample with a specified destroy date",
)
def get_destroy_sample(month: int, year: int, type: str, db: Session = Depends(get_db)):
    destroy_samples = sample_action.get_destroy_by_month_year(
        db, month, year, type, SampleModel=models.SampleReferenced
    )
    return destroy_samples


@reference_router.post(
    "/generate-destroy-report", description="Generate destroy reports"
)
def generate_destroy_reports(
    month: int,
    year: int,
    package_type: str,
    package_weight: List[schemas.DestroySampleWeight],
    db: Session = Depends(get_db),
):
    pdf, headers = sample_action.create_destroy_reports(
        db, month, year, package_type, package_weight, models.SampleReferenced
    )

    return Response(
        content=bytes(pdf.output()), media_type="application/pdf", headers=headers
    )
