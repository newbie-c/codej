import asyncpg

from passlib.hash import pbkdf2_sha256


async def create_user_record(
        conn, username, password, permissions, now):
    await conn.execute(
        '''INSERT INTO users
           (username, registered, last_visit, password_hash, permissions)
           VALUES ($1, $2, $3, $4, $5)''',
           username, now, now, pbkdf2_sha256.hash(password), permissions)
    return await conn.fetchval(
        'SELECT id FROM users WHERE username = $1', username)


async def get_conn(conf):
    if dsn := conf.get('DSN'):
        conn = await asyncpg.connect(dsn)
    else:
        conn = await asyncpg.connect(
            user=conf.get('USER'),
            database=conf.get('DB'))
    return conn
