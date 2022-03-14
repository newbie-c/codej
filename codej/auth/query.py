from datetime import datetime

from ..common.pg import create_user_record, get_conn, update_account
from .attri import initials, permissions


async def insert_permissions(conf):
    conn = await get_conn(conf)
    current = await conn.fetch('SELECT * FROM permissions')
    if current:
        for each in current:
            rem = each.get('permission')
            if rem not in permissions:
                await conn.execute(
                    'DELETE FROM permissions WHERE permission = $1', rem)
    for permission, name in zip(permissions, permissions._fields):
        p = await conn.fetchrow(
            'SELECT * FROM permissions WHERE permission = $1', permission)
        if p is None:
            await conn.execute(
                '''INSERT INTO permissions (permission, name, init)
                     VALUES ($1, $2, $3)''',
                permission,
                name.lower().replace('_', '-'),
                initials.get(permission, False))
    await conn.close()


async def check_username(conf, username):
    conn = await get_conn(conf)
    res = await conn.fetchrow(
        'SELECT username FROM users WHERE username = $1', username)
    await conn.close()
    return bool(res)


async def check_address(conf, address):
    res = False
    conn = await get_conn(conf)
    account = await conn.fetchrow(
        'SELECT address, user_id FROM accounts WHERE address = $1', address)
    swap = await conn.fetchrow(
        'SELECT swap FROM accounts WHERE swap = $1', address)
    if (account and account.get('user_id')) or swap:
        res = True
    await conn.close()
    return res


async def create_user(conf, username, address, password, perms):
    now = datetime.utcnow()
    conn = await get_conn(conf)
    user_id = await create_user_record(conn, username, password, perms, now)
    await update_account(conn, address, user_id, now)
    await conn.close()
