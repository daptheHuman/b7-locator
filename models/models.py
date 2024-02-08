from sqlalchemy import Column, Float, ForeignKey, Table, Date
from sqlalchemy.sql.sqltypes import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    product_code = Column(String(5),  primary_key=True,
                          unique=True, nullable=False)
    product_name = Column(String(255), nullable=False)
    shelf_life = Column(Float, nullable=False)
    sample = relationship("SampleRetained", backref="product",
                          cascade="all, delete-orphan")


class SampleRetained(Base):
    __tablename__ = "samples_retained"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rack_id = Column(String(5), ForeignKey("racks.rack_id"))
    product_code = Column(String(5), ForeignKey("products.product_code"))
    batch_number = Column(String(5))
    manufacturing_date = Column(Date)
    expiration_date = Column(Date)
    destroy_date = Column(Date)


class Rack(Base):
    __tablename__ = "racks"
    rack_id = Column(String(5), primary_key=True, unique=True)
    location = Column(String(255))
    sample = relationship(
        "SampleRetained", backref="rack",  cascade="all, delete-orphan")
