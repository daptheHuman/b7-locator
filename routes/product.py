from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.db import SessionLocal
from models import models
from schemas import schemas
from schemas.schemas import Product, ProductCount, ProductCreate

products_router = APIRouter(
    prefix="/products",
    tags=["products"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@products_router.get(
    "/",
    response_model=List[Product],
    description="Get a list of products by product code or retrieve all products if no product code is provided",
)
def get_all_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve products by product code or all products if no product code is provided.

    :param product_code: Optional. Product code of the product to retrieve
    :param skip: Number of products to skip (default: 0)
    :param limit: Maximum number of products to retrieve (default: 100)
    :param db: Database session dependency
    :return: List of products
    """
    products = db.query(models.Product).offset(
        skip).limit(limit).all()
    return products


@products_router.get(
    "/{product_code}",
    response_model=Product,
    description="Get a list of products by product code or retrieve all products if no product code is provided",
)
def get_products(product_code: str, db: Session = Depends(get_db)):
    """
    Retrieve products by product code or all products if no product code is provided.

    :param product_code: Optional. Product code of the product to retrieve
    :param skip: Number of products to skip (default: 0)
    :param limit: Maximum number of products to retrieve (default: 100)
    :param db: Database session dependency
    :return: List of products
    """
    product = db.query(models.Product).filter(
        models.Product.product_code == product_code).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@products_router.get("/count",  response_model=ProductCount)
def get_products_count(db: Session = Depends(get_db)):
    count_result = db.query(models.Product).count()
    return {"total": count_result}


@products_router.post("/",
                      response_model=Product)
def create_new_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product.

    :param product: Request body containing details of the new product
    :param db: Database session dependency
    :return: Details of the created product
    """
    # Create a new SampleRetained object based on the provided data
    new_product = models.Product(**product.model_dump())

    existing_product = db.query(models.Product).filter(
        models.Product.product_code == new_product.product_code).first()
    if existing_product:
        raise HTTPException(status_code=409, detail="Product already exist")

    # Add the new sample to the database session and commit the transaction
    db.add(new_product)
    db.commit()

    # Refresh the object to ensure it reflects the latest state in the database
    db.refresh(new_product)

    # Return the details of the created sample
    return [new_product]


@products_router.put("/{product_code}",
                     response_model=schemas.Product,
                     description="Update a product by Id")
def update_product_by_id(product_code: str, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    """
    Update an existing product by Id.

    :param id: Product code of the product to update
    :param product: Request body containing updated details of the product
    :param db: Database session dependency
    :return: Updated details of the product
    """
    # Retrieve the product from the database
    existing_product = db.query(models.Product).filter(
        models.Product.product_code == product_code).first()
    if existing_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update the attributes of the existing product with the new data
    for key, value in product.model_dump().items():
        setattr(existing_product, key, value)

    # Commit the transaction to save the changes
    db.commit()

    # Return the updated product
    return existing_product


@products_router.delete("/{product_code}",
                        response_model=schemas.ProductBase,
                        description="Delete a product by Id")
def delete_product_by_id(product_code: str, db: Session = Depends(get_db)):
    """
    Delete an existing product by Id.

    :param id: Product code of the product to delete
    :param db: Database session dependency
    :return: Details of the deleted product
    """
    # Retrieve the product from the database
    product_to_delete = db.query(models.Product).filter(
        models.Product.product_code == product_code).first()
    if product_to_delete is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Delete the product from the database
    db.delete(product_to_delete)
    db.commit()

    # Return the details of the deleted product
    return product_to_delete
