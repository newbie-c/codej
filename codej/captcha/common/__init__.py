from codej.common.random import randomize, randomize_lower


async def check_val(conn):
    val = await randomize_lower(5)
    while await conn.fetchrow(
            'SELECT val FROM captchas WHERE val = $1', val):
        val = await randomize_lower(5)
    return val


async def check_suffix(conn):
    suffix = await randomize(7)
    while await conn.fetchrow(
            'SELECT suffix FROM captchas WHERE suffix = $1', suffix):
        suffix = await randomize(7)
    return suffix
