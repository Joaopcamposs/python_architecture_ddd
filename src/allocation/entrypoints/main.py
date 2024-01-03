from dataclasses import asdict

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from src.allocation.domain import commands
from src.allocation.entrypoints.schemas import CreateAllocation, CreateBatch
from src.allocation.service_layer.handlers import InvalidSku
from src.allocation import bootstrap, views

app = FastAPI()
bus = bootstrap.bootstrap()


@app.post("/add_batch")
async def add_batch(
    new_batch: CreateBatch,
):
    cmd = commands.CreateBatch(
        new_batch.ref,
        new_batch.sku,
        new_batch.qty,
        new_batch.eta,
    )
    await bus.handle(cmd)
    return JSONResponse(status_code=201, content="OK")


@app.post("/allocate")
async def allocate_endpoint(
    new_allocate: CreateAllocation,
):
    try:
        cmd = commands.Allocate(
            new_allocate.orderid,
            new_allocate.sku,
            new_allocate.qty,
        )
        await bus.handle(cmd)
    except InvalidSku as e:
        raise HTTPException(detail=f"error: {e}", status_code=400)

    return JSONResponse(status_code=202, content="Ok")


@app.get("/allocations/{orderid}")
async def allocations_view_endpoint(orderid: str):
    result = await views.allocations(orderid, bus.uow)
    if not result:
        return JSONResponse(status_code=404, content="Not Found")
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
