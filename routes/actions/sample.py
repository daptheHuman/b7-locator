from fastapi import HTTPException
from sqlalchemy.orm import Session

from helpers.utils import add_years_and_months
from models import models
from schemas import schemas


def get_sample_by_id(
    db: Session,
    id: int,
    SampleModel: models.SampleReferenced | models.SampleRetained,
):
    sample = (
        db.query(SampleModel, models.Product)
        .join(models.Product)
        .filter(SampleModel.id == id)
        .one()
    )

    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    return sample


def get_all_sample(
    db: Session,
    skip: int,
    limit: int,
    SampleModel: models.SampleReferenced | models.SampleRetained,
):
    samples = db.query(SampleModel).offset(skip).limit(limit).all()

    return samples


def create_sample(
    db: Session,
    sample: schemas.SampleRetainedCreate | schemas.SampleReferencedCreate,
    SampleModel: models.SampleReferenced | models.SampleRetained,
):
    # Retrieve the product information from the database
    product = (
        db.query(models.Product)
        .filter(models.Product.product_code == sample.product_code)
        .first()
    )

    # Check if the product exists
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Calculate the expiration date by adding the shelf life to the manufacturing date
    expiration_date = add_years_and_months(
        sample.manufacturing_date, product.shelf_life
    )

    # Calculate the destroy date by adding 1 year and 1 months to the expiration date
    destroy_date = add_years_and_months(expiration_date, 1, 1)

    # Create a new SampleReferenced object with the calculated dates
    new_sample = SampleModel(
        product_code=sample.product_code,
        batch_number=sample.batch_number,
        manufacturing_date=sample.manufacturing_date,
        rack_id=sample.rack_id,
        expiration_date=expiration_date,
        destroy_date=destroy_date,
    )

    # Add the new sample to the database session and commit the transaction
    db.add(new_sample)
    db.commit()

    # Refresh the object to ensure it reflects the latest state in the database
    db.refresh(new_sample)

    # Return the details of the created sample
    return new_sample
