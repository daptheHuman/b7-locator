from datetime import date
from typing import List

from pydantic import BaseModel, Field


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


class SampleReferencedBase(BaseModel):
    product_code: str = Field("LBJAA", max_length=5)
    batch_number: str = Field("AAAAA", max_length=5)
    manufacturing_date: date
    expiration_date: date
    destroy_date: date
    rack_id: str | None = Field("A1", max_length=5)


class SampleReferencedCreate(SampleReferencedBase):
    rack_id: str = "A1"


class SampleReferenced(SampleReferencedBase):
    id: int

    class Config:
        from_attributes = True


class SampleRetainedBase(BaseModel):
    product_code: str = Field("LBJAA", max_length=5)
    batch_number: str = Field("AAAAA", max_length=5)
    manufacturing_date: date
    expiration_date: date
    destroy_date: date
    rack_id: str | None = Field("A1", max_length=5)


class SampleRetainedCreate(SampleRetainedBase):
    rack_id: str = "A1"


class SampleRetained(SampleRetainedBase):
    id: int

    class Config:
        from_attributes = True


class SampleProductJoin(SampleRetained, Product):
    pass


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


class DestructReports(BaseModel):
    samples: List[int]
