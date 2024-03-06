import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from sqlalchemy.exc import SQLAlchemyError

from config.db import SessionLocal, engine
from models import models
from models.models import Base
from routes.actions import auth_action
from routes.audit_trail import audit_router
from routes.auth import auth_router
from routes.product import products_router
from routes.rack import rack_router
from routes.sample_reference import reference_router
from routes.sample_retained import retained_router
from routes.stats import stats_router
from routes.user import users_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        print("Database schema created successfully.")
    except SQLAlchemyError as e:
        print("An error occurred while creating the database schema:", e)
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Users API",
    description="a REST API using python and mysql",
    version="0.0.1",
)

origins = os.getenv("ALLOWED_ORIGINS").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


async def db_session_middleware(request: Request, response: Response):
    response_exc = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()

        if all(
            filter not in request.url.__str__()
            for filter in ["docs", "openapi.json", "favicon.ico", "authentication"]
        ) and request.method not in ["GET", "OPTIONS"]:
            await store_audit_middleware(request, db=request.state.db)
    finally:
        request.state.db.close()

    return response_exc


async def store_audit_middleware(
    request: Request,
    db,
):
    username = request.state.username

    audit_entry = models.Audit()
    audit_entry.url = request.url.__str__()
    audit_entry.headers = username if username else ""

    audit_entry.method = request.method
    audit_entry.request = await request.body()
    db.add(audit_entry)
    db.commit()
    return audit_entry


PROTECTED = [Depends(auth_action.get_current_user), Depends(db_session_middleware)]
app.include_router(auth_router)
app.include_router(users_router, dependencies=PROTECTED)
app.include_router(audit_router, dependencies=PROTECTED)
app.include_router(products_router, dependencies=PROTECTED)
app.include_router(retained_router, dependencies=PROTECTED)
app.include_router(reference_router, dependencies=PROTECTED)
app.include_router(rack_router, dependencies=PROTECTED)
app.include_router(stats_router, dependencies=PROTECTED)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
