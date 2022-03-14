import asyncpg

from hashlib import md5

from passlib.hash import pbkdf2_sha256


async def update_account(conn, address, uid, now):
    account = await conn.fetchrow(
        'SELECT * FROM accounts WHERE address = $1', address)
    if account:
        await conn.execute(
            '''UPDATE accounts
                 SET requested = $1, user_id = $2 WHERE address = $3''',
            now, uid, address)
    else:
        await conn.execute(
            '''INSERT INTO accounts (address, ava_hash, requested, user_id)
                 VALUES ($1, $2, $3, $4)''',
            address, md5(address.encode('utf-8')).hexdigest(), now, uid)


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
