from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.allocation.adapters.orm import metadata
from src.allocation.config import create_default_database
from src.allocation.domain import commands
from src.allocation.adapters import orm
from src.allocation.entrypoints.schemas import CreateAllocation, CreateBatch
from src.allocation.service_layer import unit_of_work, messagebus
from decouple import config

from src.allocation.service_layer.handlers import InvalidSku

# dependencias de banco de dados
SQLALCHEMY_DATABASE_URL = config("DATABASE_URI")
create_default_database(SQLALCHEMY_DATABASE_URL)
orm.start_mappers()
engine = create_engine(SQLALCHEMY_DATABASE_URL)
metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/add_batch")
def add_batch(
    new_batch: CreateBatch,
):
    event = commands.CreateBatch(
        new_batch.ref,
        new_batch.sku,
        new_batch.qty,
        new_batch.eta,
    )
    messagebus.handle(event, unit_of_work.SqlAlchemyUnitOfWork())
    return JSONResponse(status_code=201, content="OK")


@app.post("/allocate")
def allocate_endpoint(
    new_allocate: CreateAllocation,
):
    try:
        event = commands.Allocate(
            new_allocate.orderid,
            new_allocate.sku,
            new_allocate.qty,
        )
        results = messagebus.handle(event, unit_of_work.SqlAlchemyUnitOfWork())
        batchref = results.pop(0)
    except InvalidSku as e:
        raise HTTPException(detail=f"error: {e}", status_code=400)

    return JSONResponse(status_code=201, content={"batchref": batchref})
