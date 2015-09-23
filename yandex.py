import asyncio
from aioauth_client import YandexClient
import settings
from datetime import datetime
import ujson


yandex = YandexClient(
    client_id=settings.client_id,
    client_secret=settings.client_secret,
    access_token=settings.access_token
)


@asyncio.coroutine
def get_counters():
    current_date = datetime.now().strftime('%Y%m%d')
    stat_url = 'https://api-metrika.yandex.ru/stat/traffic/summary.json?id={}'\
        '&date1={}'
    res = yield from yandex.request(
        'GET', 'https://api-metrika.yandex.ru/counters.json')
    data = yield from res.read()
    data = ujson.loads(data)
    counters = []
    for counter in data.get('counters', []):
        cid = counter['id']
        res = yield from yandex.request('GET', stat_url.format(cid,
                                                               current_date))
        stat = yield from res.read()
        stat = ujson.loads(stat)
        if stat['data']:
            counters.append({'name': counter['name'],
                             'visits': stat['data'][0]['visits']})
    return counters
