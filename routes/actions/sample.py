from datetime import date
from typing import List

from fastapi import HTTPException
from sqlalchemy import ARRAY, String, extract, func
from sqlalchemy.orm import Session

from helpers import utils
from helpers.utils import add_years_and_months
from models import models
from reports.pdf_generator import generate_destroy_report
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


def create_destroy_reports(
    db: Session,
    month: int,
    year: int,
    packageWeight: List[schemas.DestroyPackageAndWeight],
    SampleModel: models.SampleReferenced | models.SampleRetained,
):
    # Retrieve details for each sample
    samples = (
        db.query(
            SampleModel.product_code,
            models.Product.product_name,
            SampleModel.manufacturing_date,
            SampleModel.expiration_date,
            SampleModel.destroy_date,
            func.group_concat(SampleModel.batch_number).label("batch_numbers"),
        )
        .join(SampleModel.product)  # Join with the Product table
        .filter(extract("year", SampleModel.destroy_date) == year)
        .filter(extract("month", SampleModel.destroy_date) == month)
        .group_by(SampleModel.product_code)
        .all()
    )

    report_date = date(year, month, 1)
    if samples is None:
        raise HTTPException(status_code=404, detail="No sample found")

    # Convert the results to a dictionary with product_code as keys and merged data as values
    merged_samples = [
        schemas.DestructObject(
            product_code=sample.product_code,
            product_name=sample.product_name,
            manufacturing_date=sample.manufacturing_date,
            expiration_date=sample.expiration_date,
            destroy_date=sample.destroy_date,
            batch_numbers=utils.format_batch_numbers(sample.batch_numbers.split(",")),
        )
        for sample in samples
    ]

    for item in packageWeight:
        for sample in merged_samples:
            if sample.product_code == item.product_code:
                sample.package = item.package
                sample.weight = item.weight
                break  # Break once the product_code is found

    print(merged_samples)
    pdf, file_path = generate_destroy_report(samples=merged_samples, date=report_date)
    headers = {
        "Content-Disposition": f"attachment; filename=retained-sample_{file_path}"
    }

    return pdf, headers
