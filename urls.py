from api.handlers import counter_list

route_map = (
    ('GET', '/counters/get/', counter_list),
)
