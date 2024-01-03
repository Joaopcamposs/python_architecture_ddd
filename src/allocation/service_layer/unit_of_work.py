# pylint: disable=attribute-defined-outside-init
from __future__ import annotations

import abc
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.allocation.adapters import repository
from src.allocation import config


class AbstractUnitOfWork(abc.ABC):
    products: repository.AbstractRepository

    async def __aenter__(self) -> "AbstractUnitOfWork":
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    async def commit(self):
        await self._commit()

    def collect_new_events(self):
        for product in self.products.seen:
            while product.events:
                yield product.events.pop(0)

    @abc.abstractmethod
    async def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self):
        raise NotImplementedError


engine = create_async_engine(
    config.get_postgres_uri(),
    isolation_level="REPEATABLE READ",  # usar 'REPEATABLE READ' quando postgres real, SERIALIZABLE para sqlite
    future=True,
    echo=True,
)
DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.products = repository.SqlAlchemyRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def _commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
