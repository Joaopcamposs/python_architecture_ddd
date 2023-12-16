from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.allocation.adapters.orm import metadata
from src.allocation.domain import model
from src.allocation.adapters import orm
from src.allocation.entrypoints.schemas import CreateAllocation, CreateBatch
from src.allocation.service_layer import services, unit_of_work
from decouple import config


SQLALCHEMY_DATABASE_URL = config("DATABASE_URI")

orm.start_mappers()

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


@app.post("/add_batch")
def add_batch(
    new_batch: CreateBatch,
):
    services.add_batch(
        new_batch.ref,
        new_batch.sku,
        new_batch.qty,
        new_batch.eta,
        unit_of_work.SqlAlchemyUnitOfWork(),
    )
    return JSONResponse(status_code=201, content="OK")


@app.post("/allocate")
def allocate_endpoint(
    new_allocate: CreateAllocation,
):
    try:
        batchref = services.allocate(
            new_allocate.orderid,
            new_allocate.sku,
            new_allocate.qty,
            unit_of_work.SqlAlchemyUnitOfWork(),
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        raise HTTPException(detail=f"error: {e}", status_code=400)

    return JSONResponse(status_code=201, content={"batchref": batchref})
