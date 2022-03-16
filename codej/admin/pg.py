from datetime import datetime

from ..auth.attri import permissions
from ..common.aparsers import iter_pages, parse_last_page
from ..common.pg import create_user_record, update_account
from ..main.pg import get_group


async def create_user(conn, username, password, address):
    now = datetime.utcnow()
    perms = [each.get('permission') for each in await conn.fetch(
        'SELECT permission FROM permissions WHERE init = true')]
    user_id = await create_user_record(conn, username, password, perms, now)
    await update_account(conn, address, user_id, now)

async def select_found(conn, current, val, is_admin):
    if is_admin:
        query = await conn.fetch(
            '''SELECT username, last_visit, permissions FROM users
                 WHERE id != $1 AND username LIKE $2
                   ORDER BY last_visit DESC''',
            current, f'{val}%')
    else:
        query = await conn.fetch(
            '''SELECT username, last_visit, permissions FROM users
                 WHERE id != $1 AND username LIKE $2
                 AND permissions[1] != $3
                   ORDER BY last_visit DESC''',
            current, f'{val}%', permissions.CANNOT_LOG_IN)
    if query:
        return {'users':[
            {'username': record.get('username'),
             'last_visit': record.get('last_visit').isoformat() + 'Z',
             'group': await get_group(record.get('permissions'))}
            for record in query]}


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
