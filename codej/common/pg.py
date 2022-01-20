import asyncpg


async def get_conn(conf):
    if dsn := conf.get('DSN'):
        conn = await asyncpg.connect(dsn)
    else:
        conn = await asyncpg.connect(
            user=conf.get('USER'),
            database=conf.get('DB'))
    return conn
