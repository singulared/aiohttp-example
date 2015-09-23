import asyncio
from aiohttp import web
from utils import json_response
import ujson


@asyncio.coroutine
def counter_list(request):
    logger = request.app.logger
    logger.debug(' '.join((request.method, '-', request.path_qs)))
    counters = yield from request.app.redis.get('counters')
    if not counters:
        counters = []
    else:
        counters = ujson.loads(counters)
    return json_response(counters)
