from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel


class ProductBase(BaseModel):
    product_code: str
    product_name: str
    shelf_life: float


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    pass

    class Config:
        from_attributes = True


class ProductCount(BaseModel):
    total: int


class SampleRetainedBase(BaseModel):
    product_code: str = "LBJAA"
    batch_number: str = "FA004"
    manufacturing_date: date
    expiration_date: date
    destroy_date: date


class SampleRetainedCreate(SampleRetainedBase):
    rack_id: str = "A1"


class SampleRetained(SampleRetainedBase):
    id: int
    rack_id: str | None

    class Config:
        from_attributes = True


class RackBase(BaseModel):
    rack_id: str
    location: str


class RackCreate(RackBase):
    pass


class Rack(RackBase):
    id: int
    products: Optional[list[Product]] = []

    class Config:
        from_attributes = True
