import settings
import os
import logging
import functools
import signal
if settings.debug:
    os.environ['PYTHONASYNCIODEBUG'] = '1'
import asyncio
import aioredis
from aiohttp import web
from urls import route_map


if settings.debug:
    logging.getLogger('asyncio').setLevel(logging.DEBUG)


def app_factory():
    app = web.Application()
    app.logger = logging.getLogger('pandomim')
    ch = logging.StreamHandler()
    app.logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    app.logger.addHandler(ch)
    return app


@asyncio.coroutine
def scheduler(loop, app):
    try:
        from tasks import sync
        tasks = []
        while True:
            tasks.append(loop.create_task(sync.counter_list(loop, app)))
            yield from asyncio.sleep(settings.scheduler_delay)
    except asyncio.futures.CancelledError:
        for task in tasks:
            task.cancel()

@asyncio.coroutine
def init(loop, app, handler):

    for route in route_map:
        app.router.add_route(*route)

    app.logger.info('Create redis connection')
    app.redis = yield from aioredis.create_redis(('localhost', 6379), loop=loop)

    srv = yield from loop.create_server(handler, '127.0.0.1', 8080)
    return srv


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = app_factory()
    handler = app.make_handler()
    srv = loop.run_until_complete(init(loop, app, handler))
    app.scheduler = loop.create_task(scheduler(loop, app))
    app.logger.info('serving on {}'.format(srv.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        app.logger.info('Stop scheduler')
        app.shutdown = True
        app.scheduler.cancel()
        # loop.run_until_complete(asyncio.wait([app.scheduler]))

        app.logger.info('Server was stopped')
        loop.run_until_complete(handler.finish_connections(1.0))
        srv.close()
        loop.run_until_complete(srv.wait_closed())
        app.redis.close()
        loop.run_until_complete(app.redis.wait_closed())
        loop.run_until_complete(app.finish())
    finally:
        loop.close()
