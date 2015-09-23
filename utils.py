from aiohttp import web
import ujson


def json_response(data, **kwargs):
    # Sometimes user needs to override default content type for JSON
    kwargs.setdefault('content_type', 'application/json')
    return web.Response(body=ujson.dumps(data).encode('utf-8'), **kwargs)
