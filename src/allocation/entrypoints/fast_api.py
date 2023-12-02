from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.allocation.adapters.orm import metadata
from src.allocation.domain import model
from src.allocation.adapters import orm, repository
from src.allocation.entrypoints.schemas import CreateAllocation
from src.allocation.service_layer import services


SQLALCHEMY_DATABASE_URL = "sqlite:///././././sqlite.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

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


@app.post("/allocate")
def allocate_endpoint(
    new_allocate: CreateAllocation,
    session: Session = Depends(get_db),
):
    repo = repository.SqlAlchemyRepository(session)

    line = model.OrderLine(
        orderid=new_allocate.orderid,
        sku=new_allocate.sku,
        qty=new_allocate.qty,
    )

    try:
        batchref = services.allocate(line, repo, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        return HTTPException(detail=f"error: {e}", status_code=400)

    return {"batchref": batchref}, 201
