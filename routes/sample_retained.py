from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import extract
from sqlalchemy.orm import Session

from config.db import SessionLocal
from models import models
from reports.pdf_generator import generate_destroy_report
from schemas import schemas

retained_router = APIRouter(
    prefix="/retained",
    tags=["retained"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@retained_router.post("/",  response_model=List[schemas.SampleRetained],
                      description="Get all retained sample is stored")
def create_new_sample_retained(sample: schemas.SampleRetainedCreate, db: Session = Depends(get_db)):
    """
    Create a new retained sample.

    :param sample: Request body containing details of the new sample
    :param db: Database session dependency
    :return: Details of the created sample
    """
    # Create a new SampleRetained object based on the provided data
    new_sample = models.SampleRetained(**sample.model_dump())

    # Add the new sample to the database session and commit the transaction
    db.add(new_sample)
    db.commit()

    # Refresh the object to ensure it reflects the latest state in the database
    db.refresh(new_sample)

    # Return the details of the created sample
    return [new_sample]


@retained_router.get("/", response_model=List[schemas.SampleProductJoin],
                     description="Get all retained sample")
def get_retained_samples_for_product(id: str = "", skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve retained samples associated with a specific product, or all retained samples if product_code isn't specified.


    :param db: Database session dependency
    :return: List of retained samples for the specified product
    """
    # Query the database to retrieve retained samples for the specified product
    if id:
        retained_samples = db.query(models.SampleRetained, models.Product).join(models.Product).filter(
            models.SampleRetained.id == id).one()
        if not retained_samples:
            raise HTTPException(
                status_code=404, detail="Retained samples not found")

    else:
        retained_samples = db.query(
            models.SampleRetained).offset(skip).limit(limit).all()

    retained_samples = [{
        "id": sample.id,
        "product_code": sample.product_code,
        "batch_number": sample.batch_number,
        "manufacturing_date": sample.manufacturing_date,
        "expiration_date": sample.expiration_date,
        "destroy_date": sample.destroy_date,
        "rack_id": sample.rack_id,
        "product_name": sample.product.product_name,
        "shelf_life": sample.product.shelf_life
    } for sample in retained_samples]

    return retained_samples


@retained_router.put("/{id}", response_model=schemas.SampleRetained,
                     description="Update a retained sample by ID")
def update_retained_sample(id: str, sample: schemas.SampleRetained, db: Session = Depends(get_db)):
    """
    Update an existing retained sample by ID.

    :param id: ID of the retained sample to update
    :param sample: Request body containing updated details of the retained sample
    :param db: Database session dependency
    :return: Updated details of the retained sample
    """
    # Retrieve the retained sample from the database
    existing_sample = db.query(models.SampleRetained).filter(
        models.SampleRetained.id == id).first()
    if existing_sample is None:
        raise HTTPException(
            status_code=404, detail="Retained sample not found")

    # Update the attributes of the existing sample with the new data
    for key, value in sample.model_dump().items():
        setattr(existing_sample, key, value)

    # Commit the transaction to save the changes
    db.commit()

    # Return the updated retained sample
    return existing_sample


@retained_router.delete("/{id}", response_model=schemas.SampleRetained,
                        description="Delete a retained sample by ID")
def delete_retained_sample(id: str, db: Session = Depends(get_db)):
    """
    Delete an existing retained sample by ID.

    :param id: ID of the retained sample to delete
    :param db: Database session dependency
    :return: Details of the deleted retained sample
    """
    # Retrieve the retained sample from the database
    sample_to_delete = db.query(models.SampleRetained).filter(
        models.SampleRetained.id == id).first()
    if sample_to_delete is None:
        raise HTTPException(
            status_code=404, detail="Retained sample not found")

    # Delete the retained sample from the database
    db.delete(sample_to_delete)
    db.commit()

    # Return the details of the deleted retained sample
    return sample_to_delete


@retained_router.get("/manufacturing",  response_model=List[schemas.SampleRetainedBase],
                     description="Get a product with a specified manufacturing date")
def get_manufacturing_products(db: Session = Depends(get_db), date: date = Query(default=date.today())):
    products = db.query(models.SampleRetained).where(
        models.SampleRetained.manufacturing_date == date)
    if products is None:
        raise HTTPException(status_code=404, detail="No product found")

    return products


@retained_router.get("/expired",  response_model=List[schemas.SampleRetainedBase],
                     description="Get a product with a specified expired date")
def get_expired_products(db: Session = Depends(get_db), date: date = Query(default=date.today())):
    products = db.query(models.SampleRetained).where(
        models.SampleRetained.expiration_date == date)
    if products is None:
        raise HTTPException(status_code=404, detail="No product found")

    return products


@retained_router.get("/destroy",  response_model=List[schemas.SampleProductJoin],
                     description="Get a product with a specified destroy date")
def get_destroy_sample(month: int, year: int, db: Session = Depends(get_db)):
    print(month, year)
    samples = db.query(models.SampleRetained).filter(extract('year', models.SampleRetained.destroy_date) == year).filter(
        extract('month', models.SampleRetained.destroy_date) == month).all()

    if samples is None:
        raise HTTPException(status_code=404, detail="No sample found")

    retained_samples = [{
        "id": sample.id,
        "product_code": sample.product_code,
        "batch_number": sample.batch_number,
        "manufacturing_date": sample.manufacturing_date,
        "expiration_date": sample.expiration_date,
        "destroy_date": sample.destroy_date,
        "rack_id": sample.rack_id,
        "product_name": sample.product.product_name,
        "shelf_life": sample.product.shelf_life
    } for sample in samples]

    return retained_samples


@retained_router.get("/generate-destroy-report", description="Generate destroy reports")
def generate_destroy_reports(month: int, year: int, db: Session = Depends(get_db)):
    # Retrieve details for each sample
    samples = db.query(models.SampleRetained).filter(extract('year', models.SampleRetained.destroy_date) == year).filter(
        extract('month', models.SampleRetained.destroy_date) == month)
    report_date = date(year, month, 1)
    if samples is None:
        raise HTTPException(status_code=404, detail="No sample found")

    sample_referenced = [schemas.SampleProductJoin(id=sample.id,
                                                   product_code=sample.product_code,
                                                   product_name=sample.product.product_name,
                                                   shelf_life=sample.product.shelf_life,
                                                   batch_number=sample.batch_number,
                                                   manufacturing_date=sample.manufacturing_date,
                                                   expiration_date=sample.expiration_date,
                                                   destroy_date=sample.destroy_date,
                                                   rack_id=sample.rack_id
                                                   )for sample in samples]

    pdf, file_path = generate_destroy_report(
        samples=sample_referenced, date=report_date)
    headers = {
        "Content-Disposition": f"attachment; filename=retained-sample_{file_path}"
    }

    return Response(content=bytes(pdf.output()), media_type="application/pdf", headers=headers)
