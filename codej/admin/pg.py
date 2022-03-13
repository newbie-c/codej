from datetime import datetime
from hashlib import md5

from passlib.hash import pbkdf2_sha256

from ..auth.attri import permissions
from ..common.aparsers import iter_pages, parse_last_page
from ..main.pg import get_group


async def create_user(conn, username, password, address):
    now = datetime.utcnow()
    perms = [each.get('permission') for each in await conn.fetch(
        'SELECT permission FROM permissions WHERE init = true')]
    await conn.execute(
        '''INSERT INTO users
             (username, registered, last_visit, password_hash, permissions)
             VALUES ($1, $2, $3, $4, $5)''',
        username, now, now,
        pbkdf2_sha256.hash(password), perms)
    acc = await conn.fetchval(
        'SELECT id FROM accounts WHERE address = $1', address)
    user_id = await conn.fetchval(
        'SELECT id FROM users WHERE username = $1', username)
    if acc:
        await conn.execute(
            'UPDATE accounts SET user_id = $1, requested = $2 WHERE id = $3',
            user_id, now, acc)
    else:
        await conn.execute(
            '''INSERT INTO accounts (address, ava_hash, requested, user_id)
                 VALUES ($1, $2, $3, $4)''',
            address, md5(address.encode('utf-8')).hexdigest(), now, user_id)


async def select_users(conn, current, page, per_page, last, is_admin):
    if is_admin:
        query = await conn.fetch(
            '''SELECT username, last_visit, permissions
                 FROM users WHERE id != $1
                 ORDER BY last_visit DESC LIMIT $2 OFFSET $3''',
            current, per_page, per_page*(page-1))
    else:
        query = await conn.fetch(
            '''SELECT username, last_visit, permissions
                 FROM users WHERE id != $1 AND permissions[1] != $2
                 ORDER BY last_visit DESC LIMIT $3 OFFSET $4''',
            current, permissions.CANNOT_LOG_IN, per_page, per_page*(page-1))
    if query:
        return {'page': page,
                'next': page + 1 if page + 1 <= last else None,
                'prev': page - 1 or None,
                'pages': await iter_pages(page, last),
                'users': [
                    {'username': record.get('username'),
                     'last_visit': record.get('last_visit').isoformat() + 'Z',
                     'group': await get_group(record.get('permissions'))}
                    for record in query]}


async def check_last_users(conn, current, page, per_page, is_admin):
    if is_admin:
        q = 'SELECT count(*) FROM users WHERE id != $1'
        num = await conn.fetchval(q, current)
    else:
        q = '''SELECT count(*) FROM users
                 WHERE id != $1 AND permissions[1] != $2'''
        num = await conn.fetchval(q, current, permissions.CANNOT_LOG_IN)
    return await parse_last_page(page, per_page, num)
