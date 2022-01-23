from ..common.random import randomize


async def get_unique(conn, prefix, num):
    while True:
        res = prefix + await randomize(num)
        if await conn.exists(res):
            continue
        return res


async def assign_cache(rc, prefix, suffix, val, expiration):
    cache = await get_unique(rc, prefix, 6)
    await rc.hmset(cache, {'suffix': suffix, 'val': val})
    await rc.expire(cache, expiration)
    return cache


async def extract_cache(rc, cache):
    suffix, val = await rc.hmget(cache, 'suffix', 'val')
    return suffix, val


async def assign_uid(rc, prefix, remember_me, user):
    if remember_me:
        expiration = 30 * 24 * 60 * 60
    else:
        expiration = 2 * 60 * 60
    cache = await get_unique(rc, prefix, 9)
    await rc.set(cache, user.get('id'))
    await rc.expire(cache, expiration)
    return cache
