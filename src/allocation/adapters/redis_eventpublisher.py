import json
import logging
from dataclasses import asdict

import redis

from src.allocation import config
from src.allocation.domain import events


logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())


def publish(channel, event: events.Event):  # (1)
    logging.debug("publishing: channel=%s, event=%s", channel, event)
    r.publish(channel, json.dumps(asdict(event)))


def update_readmodel(orderid, sku, batchref):
    r.hset(orderid, sku, batchref)


def get_readmodel(orderid):
    return r.hgetall(orderid)
