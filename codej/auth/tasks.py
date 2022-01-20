import asyncio
import functools

from ..common.pg import get_conn
from ..captcha.common import check_val
from ..captcha.picturize.picture import generate_image


async def change_pattern(conf, suffix):
    conn = await get_conn(conf)
    #conn = await asyncpg.connect(
    #    user=conf.get('DBU'),
    #    database=conf.get('DB'))
    val = await check_val(conn)
    loop = asyncio.get_running_loop()
    pic = await loop.run_in_executor(
        None, functools.partial(generate_image, val))
    await conn.execute(
        'UPDATE captchas SET val = $1, picture = $2 WHERE suffix = $3',
        val, pic.read(), suffix)
    pic.close()
    await conn.close()
    return None