from typing import List

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from config.db import SessionLocal
from models import models
from routes.actions import auth_action, sample
from schemas import schemas

retained_router = APIRouter(prefix="/retained", tags=["retained"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@retained_router.post(
    "/",
    response_model=List[schemas.Sample],
    description="Get all retained sample is stored",
)
def create_new_sample_retained(
    sample_detail: schemas.SampleCreate, db: Session = Depends(get_db)
):
    """
    Create a new retained sample.

    :param sample: Request body containing details of the new sample
    :param db: Database session dependency
    :return: Details of the created sample
    """
    new_sample = sample.create_sample(
        db, sample=sample_detail, SampleModel=models.SampleRetained
    )
    return [new_sample]


@retained_router.get(
    "/",
    response_model=List[schemas.SampleProductJoin],
    description="Get all retained sample",
)
def get_retained_samples_for_product(
    id: str = "", skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """
    Retrieve retained samples associated with a specific product, or all retained samples if product_code isn't specified.


    :param db: Database session dependency
    :return: List of retained samples for the specified product
    """
    # Query the database to retrieve retained samples for the specified product
    if id:
        retained_samples = sample.get_sample_by_id(
            db, id, SampleModel=models.SampleRetained
        )
    else:
        retained_samples = sample.get_all_sample(
            db, skip, limit, SampleModel=models.SampleRetained
        )
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
        for sample in retained_samples
    ]

    return samples


@retained_router.put(
    "/{id}",
    response_model=schemas.SampleUpdate,
    description="Update a retained sample by ID",
    dependencies=[Depends(auth_action.is_admin)],
)
def update_retained_sample(
    id: str, updated_sample: schemas.SampleUpdate, db: Session = Depends(get_db)
):
    """
    Update an existing retained sample by ID.

    :param id: ID of the retained sample to update
    :param sample: Request body containing updated details of the retained sample
    :param db: Database session dependency
    :return: Updated details of the retained sample
    """
    updated_sample = sample.update_sample(
        db, id, updated_sample, SampleModel=models.SampleRetained
    )

    # Return the updated retained sample
    return updated_sample


@retained_router.delete(
    "/{id}",
    response_model=schemas.Sample,
    description="Delete a retained sample by ID",
    dependencies=[Depends(auth_action.is_admin)],
)
def delete_retained_sample(id: str, db: Session = Depends(get_db)):
    """
    Delete an existing retained sample by ID.

    :param id: ID of the retained sample to delete
    :param db: Database session dependency
    :return: Details of the deleted retained sample
    """
    deleted_sample = sample.delete_sample(db, id, SampleModel=models.SampleRetained)

    # Return the details of the deleted retained sample
    return deleted_sample


@retained_router.get(
    "/destroy",
    response_model=List[schemas.SampleProductJoin],
    description="Get a product with a specified destroy date",
)
def get_destroy_sample(month: int, year: int, db: Session = Depends(get_db)):
    destroy_samples = sample.get_destroy_by_month_year(
        db, month, year, SampleModel=models.SampleRetained
    )
    return destroy_samples


@retained_router.post(
    "/generate-destroy-report", description="Generate destroy reports"
)
def generate_destroy_reports(
    month: int,
    year: int,
    package_weight: List[schemas.DestroyPackageAndWeight],
    db: Session = Depends(get_db),
):
    pdf, headers = sample.create_destroy_reports(
        db, month, year, package_weight, models.SampleRetained
    )

    return Response(
        content=bytes(pdf.output()), media_type="application/pdf", headers=headers
    )
