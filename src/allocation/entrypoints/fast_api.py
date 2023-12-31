from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from src.allocation.adapters.orm import metadata
from src.allocation.domain import commands
from src.allocation.adapters import orm
from src.allocation.entrypoints.schemas import CreateAllocation, CreateBatch
from src.allocation.service_layer import unit_of_work, messagebus
from src.allocation.service_layer.handlers import InvalidSku
from src.allocation.service_layer.unit_of_work import engine

app = FastAPI()
orm.start_mappers()
metadata.create_all(bind=engine)


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
