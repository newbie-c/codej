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
    user_ = {'id': user.get('id'),
             'username': user.get('username'),
             'registered': user.get('registered').isoformat() + 'Z',
             'ava': user.get('ava_hash'),
             'tape': user.get('tape') or 0,
             'author': user.get('author') or 0}
    if await rc.exists(f'perm:{user.get("id")}'):
        await rc.delete(f'perm:{user.get("id")}')
    for perm in user.get('permissions'):
        await rc.rpush(f'perm:{user.get("id")}', perm)
    if remember_me:
        expiration = 30 * 24 * 60 * 60
    else:
        expiration = 2 * 60 * 60
    cache = await get_unique(rc, prefix, 9)
    await rc.hmset(cache, user_)
    await rc.expire(cache, expiration)
    await rc.expire(f'perm:{user.get("id")}', 30*24*60*60)
    return cache
