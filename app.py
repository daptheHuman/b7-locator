from fastapi import FastAPI
import uvicorn
from models.models import Base
from config.db import engine
from routes.product import products_router
from routes.sample_retained import retained_router
from sqlalchemy.exc import SQLAlchemyError


try:
    Base.metadata.create_all(bind=engine)
    print("Database schema created successfully.")
except SQLAlchemyError as e:
    print("An error occurred while creating the database schema:", e)


app = FastAPI(
    title="Users API",
    description="a REST API using python and mysql",
    version="0.0.1",
)

app.include_router(products_router)
app.include_router(retained_router)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
