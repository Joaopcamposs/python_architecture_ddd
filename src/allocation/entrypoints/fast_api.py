from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from src.allocation.adapters.orm import metadata
from src.allocation.domain import commands
from src.allocation.entrypoints.schemas import CreateAllocation, CreateBatch
from src.allocation.service_layer import unit_of_work, messagebus
from src.allocation.service_layer.handlers import InvalidSku
from src.allocation.service_layer.unit_of_work import engine
from src.allocation import bootstrap, views

app = FastAPI()
bus = bootstrap.bootstrap()
# metadata.create_all(bind=engine)  # todo rever e é necessário para execucao principal


@app.post("/add_batch")
def add_batch(
    new_batch: CreateBatch,
):
    cmd = commands.CreateBatch(
        new_batch.ref,
        new_batch.sku,
        new_batch.qty,
        new_batch.eta,
    )
    bus.handle(cmd)
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


@app.get("/allocations/{orderid}")
def allocations_view_endpoint(orderid: str):
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    result = views.allocations(orderid, uow)
    if not result:
        return JSONResponse(status_code=404, content="Not Found")
    return JSONResponse(status_code=201, content=result)
