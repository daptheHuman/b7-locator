from datetime import date, datetime
from re import L
from typing import List, Optional
from pydantic import BaseModel


class ProductBase(BaseModel):
    product_name: str
    shelf_life: float


class ProductCreate(ProductBase):
    product_code: str
    pass


class ProductUpdate(ProductBase):
    pass


class Product(ProductBase):
    product_code: str

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
    rack_id: str | None


class SampleRetainedCreate(SampleRetainedBase):
    rack_id: str = "A1"


class SampleRetained(SampleRetainedBase):
    id: int

    class Config:
        from_attributes = True


class RackBase(BaseModel):
    location: str


class RackCreate(RackBase):
    rack_id: str


class RackUpdate(RackBase):
    location: str


class Rack(RackBase):
    rack_id: str

    class Config:
        from_attributes = True
