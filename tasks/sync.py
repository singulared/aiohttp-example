import asyncio
import time
import ujson
from yandex import get_counters


@asyncio.coroutine
def counter_list(loop, app):
    try:
        app.logger.debug('sync.counter_list - started')
        yield from asyncio.sleep(10)
        counters = yield from get_counters()
        yield from app.redis.set('counters', ujson.dumps(counters))
        app.logger.debug('sync.counter_list - ended')
    except asyncio.futures.CancelledError:
        app.logger.debug('sync.counter_list - cancelled')
