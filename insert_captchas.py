import argparse
import asyncio
import functools

import asyncpg

from codej import settings
from codej.captcha.common import check_suffix, check_val
from codej.captcha.picturize.picture import generate_image


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument(
        '-n',
        action='store',
        dest='num',
        type=int,
        default=1000,
        help='control the number of created captchas')
    return args.parse_args()


async def gen_row():
    conn = await asyncpg.connect(settings.get('DB'))
    val = await check_val(conn)
    suffix = await check_suffix(conn)
    loop = asyncio.get_running_loop()
    pic = await loop.run_in_executor(
        None, functools.partial(generate_image, val))
    await conn.execute(
        'INSERT INTO captchas (picture, val, suffix) VALUES ($1, $2, $3)',
        pic.read(), val, suffix)
    await conn.close()
    pic.close()
    print(val, suffix)


async def main(num):
    for _ in range(num):
        row = asyncio.create_task(gen_row())
        await row


if __name__ == '__main__':
    arguments = parse_args()
    asyncio.run(main(arguments.num))
