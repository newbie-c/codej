from validate_email import validate_email

from .attri import permissions


async def filter_user(conn, login):
    squery = '''SELECT users.id AS id,
                       users.username AS username,
                       users.password_hash AS password_hash,
                       users.permissions AS permissions
                  FROM users, accounts WHERE users.id = accounts.user_id'''
    if validate_email(login):
        squery += ' AND accounts.address = $1'
    else:
        squery += ' AND users.username = $1'
    query = await conn.fetchrow(squery, login)
    if query and permissions.CANNOT_LOG_IN not in query.get('permissions'):
        return {'id': query.get('id'),
                'username': query.get('username'),
                'password_hash': query.get('password_hash')}
