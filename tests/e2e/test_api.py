import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.allocation.adapters.orm import metadata
from src.allocation.entrypoints.fast_api import app, get_db

# configurando api de testes
SQLALCHEMY_DATABASE_URL = "sqlite:///././sqlite.db"
# orm.start_mappers()
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        return db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"


def post_to_add_batch(ref, sku, qty, eta):
    response = client.post(
        "/add_batch", json={"ref": ref, "sku": sku, "qty": qty, "eta": eta}
    )
    assert response.status_code == 201


def test_happy_path_returns_201_and_allocated_batch():
    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    post_to_add_batch(laterbatch, sku, 100, "2011-01-02")
    post_to_add_batch(earlybatch, sku, 100, "2011-01-01")
    post_to_add_batch(otherbatch, othersku, 100, None)
    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}

    response = client.post("/allocate", json=data)

    assert response.status_code == 201
    assert response.json()["batchref"] == earlybatch


def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, orderid = random_sku(), random_orderid()
    data = {"orderid": orderid, "sku": unknown_sku, "qty": 20}

    response = client.post("/allocate", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == f"error: Invalid sku {unknown_sku}"
