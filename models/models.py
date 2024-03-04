from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer, String

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255))
    password = Column(String(255))
    is_admin = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Audit(Base):
    __tablename__ = "audit"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255))
    headers = Column(String(255))
    method = Column(String(255))
    request = Column(String(255))
    response = Column(String(255))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class Product(Base):
    __tablename__ = "products"

    product_code = Column(String(5), primary_key=True, unique=True, nullable=False)
    product_name = Column(String(255), nullable=False)
    shelf_life = Column(Float, nullable=False)
    retained_sample = relationship(
        "SampleRetained", back_populates="product", cascade="all, delete-orphan"
    )
    referenced_sample = relationship(
        "SampleReferenced", back_populates="product", cascade="all, delete-orphan"
    )


class SampleRetained(Base):
    __tablename__ = "samples_retained"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rack_id = Column(String(5), ForeignKey("racks.rack_id"))
    product_code = Column(String(5), ForeignKey("products.product_code"))
    batch_number = Column(String(5))
    manufacturing_date = Column(Date)
    expiration_date = Column(Date)
    destroy_date = Column(Date)
    product = relationship("Product", back_populates="retained_sample")
    rack = relationship("Rack", back_populates="retained_sample")


class SampleReferenced(Base):
    __tablename__ = "samples_referenced"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rack_id = Column(String(5), ForeignKey("racks.rack_id"))
    product_code = Column(String(5), ForeignKey("products.product_code"))
    batch_number = Column(String(5))
    manufacturing_date = Column(Date)
    expiration_date = Column(Date)
    destroy_date = Column(Date)
    product = relationship("Product", back_populates="referenced_sample")
    rack = relationship("Rack", back_populates="referenced_sample")


class Rack(Base):
    __tablename__ = "racks"
    rack_id = Column(String(5), primary_key=True, unique=True)
    max_stored = Column(Integer, nullable=False)
    location = Column(String(255))
    retained_sample = relationship(
        "SampleRetained", back_populates="rack", cascade="all, delete-orphan"
    )
    referenced_sample = relationship(
        "SampleReferenced", back_populates="rack", cascade="all, delete-orphan"
    )
