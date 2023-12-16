import abc

from src.allocation.domain import model


class AbstractProductRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, product: model.Product):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, sku) -> model.Product:
        raise NotImplementedError


class SqlAlchemyProductRepository(AbstractProductRepository):
    def __init__(self, session):
        self.session = session

    def add(self, product):
        self.session.add(product)

    def get(self, sku):
        return (
            self.session.query(model.Product)
            .filter_by(sku=sku)
            .with_for_update()  # controle de simultaneidade pessimista: SELECT FOR UPDATE
            .first()
        )
