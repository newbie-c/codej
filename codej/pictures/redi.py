from ..auth.redi import get_unique


async def assign_pic_cache(conn, data, prefix='pic:', name=None):
    if prefix:
        cache = await get_unique(conn, prefix, 6)
        await conn.hmset(cache, data)
        await conn.expire(cache, 180)
        return cache
    await conn.hmset(name, data)
    await conn.expire(name, 180)
    return name
