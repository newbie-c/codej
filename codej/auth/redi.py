import aioredis

from ..common.random import randomize


async def get_unique(conn, prefix, num):
    while True:
        res = prefix + await randomize(num)
        if await conn.exists(res):
            continue
        return res


async def assign_cache(rdb, prefix, suffix, val, expiration):
    rc = await aioredis.from_url(rdb)
    cache = await get_unique(rc, prefix, 6)
    await rc.hmset(cache, {'suffix': suffix, 'val': val})
    await rc.expire(cache, expiration)
    await rc.close()
    return cache
