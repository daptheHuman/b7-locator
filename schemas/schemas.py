from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    product_name: str
    shelf_life: float
    product_code: str


class ProductCreate(ProductBase):
    product_code: str = Field("AAAAA", max_length=5)
    pass


class ProductUpdate(ProductBase):
    pass


class Product(ProductBase):
    pass

    class Config:
        from_attributes = True


class ProductCount(BaseModel):
    total: int


class SampleBase(BaseModel):
    product_code: str = Field("LBJAA", max_length=5)
    batch_number: str = Field("AAAAA", max_length=5)
    manufacturing_date: date
    expiration_date: date
    destroy_date: date
    rack_id: str | None = Field("A1", max_length=5)


class SampleCreate(BaseModel):
    # Override the attributes to accept only product_code, batch_number, and manufacturing_date
    product_code: str
    batch_number: str
    manufacturing_date: date
    rack_id: str | None


class SampleUpdate(BaseModel):
    product_code: Optional[str] = Field(None, max_length=5)
    batch_number: Optional[str] = Field(None, max_length=5)
    manufacturing_date: Optional[date] = Field(None)
    expiration_date: Optional[date] = Field(None)
    destroy_date: Optional[date] = Field(None)
    rack_id: Optional[str] = Field(None, max_length=5)
    id: Optional[int] = Field(None)


class Sample(SampleBase):
    id: int

    class Config:
        from_attributes = True


class SampleBase(BaseModel):
    product_code: str = Field("LBJAA", max_length=5)
    batch_number: str = Field("AAAAA", max_length=5)
    manufacturing_date: date | None
    expiration_date: date | None
    destroy_date: date | None
    rack_id: str | None = Field("A1", max_length=5)


class SampleProductJoin(Sample, Product):
    pass


class RackBase(BaseModel):
    location: str
    max_stored: int


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


class DestructObject(BaseModel):
    product_code: str
    product_name: str
    manufacturing_date: date
    expiration_date: date
    destroy_date: date
    batch_numbers: str
    package: str = ""
    weight: float = 0.0


class DestroyPackageAndWeight(BaseModel):
    product_code: str
    package: str
    weight: float
