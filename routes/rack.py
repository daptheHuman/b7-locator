from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.db import SessionLocal
from models import models
from schemas import schemas

rack_router = APIRouter(
    prefix="/rack",
    tags=["rack"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@rack_router.post("/",  response_model=List[schemas.Rack],
                  description="Create a new rack")
def create_new_rack(sample: schemas.RackCreate, db: Session = Depends(get_db)):
    """
    Create a new rack.

    :param sample: Request body containing details of the new sample
    :param db: Database session dependency
    :return: Details of the created sample
    """
    # Create a new SampleRetained object based on the provided data
    new_rack = models.Rack(**sample.model_dump())
    
    existing_rack = db.query(models.Rack).filter(
        models.Rack.rack_id == new_rack.rack_id).first()
    if existing_rack:
        raise HTTPException(status_code=409, detail="Rack already exist")

    # Add the new sample to the database session and commit the transaction
    db.add(new_rack)
    db.commit()

    # Refresh the object to ensure it reflects the latest state in the database
    db.refresh(new_rack)

    # Return the details of the created sample
    return [new_rack]


@rack_router.get("/", response_model=List[schemas.Rack],
                 description="Get all product retained sample")
def get_all_racks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    :param db: Database session dependency
    :return: List of retained samples for the specified product
    """
    # Query the database to retrieve retained samples for the specified product
    racks = db.query(
        models.Rack).offset(skip).limit(limit).all()
    return racks


@rack_router.get("/{rack_id}", response_model=List[schemas.Rack],
                 description="Get specified rack")
def get_specified_rack(rack_id: str, db: Session = Depends(get_db)):
    """
    :param rack_id: Rack rack_id of the rack 
    :param db: Database session dependency
    :return: List of retained samples for the specified product
    """
    # Query the database to retrieve retained samples for the specified product
    racks = db.query(
        models.Rack).where(models.Rack.rack_id == rack_id).all()
    return racks


@rack_router.put("/{rack_id}",
                 response_model=schemas.Rack,
                 description="Update a rack by Id")
def update_rack_by_id(rack_id: str, rack: schemas.RackCreate, db: Session = Depends(get_db)):
    """
    Update an existing rack by Id.

    :param id: Product code of the product to update
    :param product: Request body containing updated details of the product
    :param db: Database session dependency
    :return: Updated details of the product
    """
    # Retrieve the product from the database
    existing_rack = db.query(models.Rack).filter(
        models.Rack.rack_id == rack_id).first()
    if existing_rack is None:
        raise HTTPException(status_code=404, detail="Rack not found")

    # Update the attributes of the existing product with the new data
    for key, value in rack.model_dump().items():
        setattr(existing_rack, key, value)

    # Commit the transaction to save the changes
    db.commit()

    # Return the updated product
    return existing_rack


@rack_router.delete("/{rack_id}",
                    response_model=schemas.Rack,
                    description="Delete a rack by Id")
def delete_product_by_id(rack_id: str, db: Session = Depends(get_db)):
    """
    Delete an existing product by Id.

    :param id: Product code of the product to delete
    :param db: Database session dependency
    :return: Details of the deleted product
    """
    # Retrieve the product from the database
    rack_to_delete = db.query(models.Rack).filter(
        models.Rack.rack_id == rack_id).first()
    if rack_to_delete is None:
        raise HTTPException(status_code=404, detail="Rack not found")

    # Delete the product from the database
    db.delete(rack_to_delete)
    db.commit()

    # Return the details of the deleted product
    return rack_to_delete
