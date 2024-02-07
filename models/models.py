from shelve import Shelf
import shelve
from sqlalchemy import Column, Float, ForeignKey, Table, Date
from sqlalchemy.sql.sqltypes import Integer, String
from sqlalchemy.orm import relationship

from config.db import Base


class Product(Base):
    __tablename__ = "products"

    product_code = Column(String(5),  primary_key=True,
                          unique=True, nullable=False)
    product_name = Column(String(255), nullable=False)
    shelf_life = Column(Float, nullable=False)
    # One-to-Many relationship
    samples_retained = relationship(
        "SampleRetained", back_populates="product")


class SampleRetained(Base):
    __tablename__ = "samples_retained"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_code = Column(String(5), ForeignKey("products.product_code"))
    batch_number = Column(String(5))
    manufacturing_date = Column(Date)
    expiration_date = Column(Date)
    destroy_date = Column(Date)
    # Establishing many-to-one relationship with Product
    product = relationship("Product", back_populates="samples_retained")
    rack_id = Column(String(5), ForeignKey("racks.rack_id"))


class Rack(Base):
    __tablename__ = "racks"
    rack_id = Column(String(5), primary_key=True, unique=True)
    # Assuming location as a string for simplicity
    location = Column(String(255))
