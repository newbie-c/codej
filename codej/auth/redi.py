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
    data = f'data:{user.get("id")}'
    existed = await rc.exists(data)
    await rc.hmset(
        data, {'id': user.get('id'),
               'username': user.get('username'),
               'registered': f"{user.get('registered').isoformat()}Z",
               'permissions': ','.join(user.get('permissions')),
               'ava': user.get('ava'),
               'many': 0})
    if existed:
        await rc.hset(data, key='many', value=1)
        if remember_me:
            await rc.persist(data)
            await rc.expire(data, expiration)
        else:
            if await rc.ttl(data) < expiration:
                await rc.persist(data)
                await rc.expire(data, expiration)
    else:
        await rc.expire(data, expiration)
    return cache
