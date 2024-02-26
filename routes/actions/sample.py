from datetime import date
from typing import List

from fastapi import HTTPException
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from helpers import utils
from helpers.utils import add_years_and_months
from models import models
from reports.pdf_generator import generate_destroy_report
from routes.actions.rack import get_rack_by_id
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


def get_destroy_by_month_year(
    db: Session,
    month: int,
    year: int,
    SampleModel: models.SampleReferenced | models.SampleRetained,
):
    samples = (
        db.query(SampleModel)
        .filter(extract("year", SampleModel.destroy_date) == year)
        .filter(extract("month", SampleModel.destroy_date) == month)
        .all()
    )

    if samples is None:
        raise HTTPException(status_code=404, detail="No sample found")

    samples = [
        schemas.SampleProductJoin(
            id=sample.id,
            product_code=sample.product_code,
            batch_number=sample.batch_number,
            manufacturing_date=sample.manufacturing_date,
            expiration_date=sample.expiration_date,
            destroy_date=sample.destroy_date,
            rack_id=sample.rack_id,
            product_name=sample.product.product_name,
            shelf_life=sample.product.shelf_life,
        )
        for sample in samples
    ]
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

    if sample.rack_id:
        rack = get_rack_by_id(sample.rack_id)
        if rack.max_stored > len(rack.retained_sample):  # Check if capacity available
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

            return new_sample
        else:
            raise HTTPException(status_code=400, detail="Rack capacity exceeded")

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


def update_sample(
    db: Session,
    id: str,
    updated_sample: schemas.SampleUpdate,
    SampleModel: models.SampleRetained | models.SampleReferenced,
):
    # Retrieve the sample from the database
    existing_sample = db.query(SampleModel).filter(SampleModel.id == id)
    if existing_sample is None:
        raise HTTPException(status_code=404, detail="Retained sample not found")

    original_rack_id = existing_sample.first().rack_id
    new_rack_id = updated_sample.rack_id

    if new_rack_id != original_rack_id:
        # Check capacity of the new rack (if provided)
        if new_rack_id:
            new_rack = get_rack_by_id(db, new_rack_id)
            if new_rack and new_rack.max_stored <= len(new_rack.retained_sample) + len(
                new_rack.referenced_sample
            ):
                raise HTTPException(status_code=400, detail="Rack capacity exceeded")

    # Update sample attributes
    existing_sample.update(updated_sample.model_dump())

    # Commit the transaction to save the changes
    db.commit()

    # Return the updated sample
    return updated_sample


def delete_sample(
    db: Session, id: str, SampleModel: models.SampleRetained | models.SampleReferenced
):
    sample_to_delete = db.query(SampleModel).filter(SampleModel.id == id).first()
    if sample_to_delete is None:
        raise HTTPException(status_code=404, detail="Sample not found")

    # Delete the sample from the database
    db.delete(sample_to_delete)
    db.commit()

    # Return the details of the deleted sample
    return sample_to_delete


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

    pdf, file_path = generate_destroy_report(samples=merged_samples, date=report_date)
    headers = {
        "Content-Disposition": f"attachment; filename={SampleModel.__tablename__}-{file_path}"
    }

    return pdf, headers
