import sys
import os
import asyncio
import json
import logging
import redis.asyncio as redis

# Adicione o diretório raiz ao caminho do Python
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
)
from src.allocation import config, bootstrap
from src.allocation.domain import commands

logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())


async def main():
    logger.info("Redis pubsub starting")
    bus = bootstrap.bootstrap()
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe("change_batch_quantity")

    async for m in pubsub.listen():
        await handle_change_batch_quantity(m, bus)


async def handle_change_batch_quantity(m, bus):
    logger.info("handling %s", m)
    data = json.loads(m["data"])
    cmd = commands.ChangeBatchQuantity(ref=data["batchref"], qty=data["qty"])
    await bus.handle(cmd)


if __name__ == "__main__":
    asyncio.run(main())
