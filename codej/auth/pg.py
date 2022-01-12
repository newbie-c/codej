from validate_email import validate_email


async def filter_user(conn, login):
    squery = '''SELECT users.id AS id,
                       users.username AS username,
                       users.registered AS registered,
                       users.password_hash AS password_hash,
                       users.permissions AS permissions,
                       accounts.ava_hash AS ava_hash
                  FROM users, accounts WHERE users.id = accounts.user_id'''
    if validate_email(login):
        squery += ' AND accounts.address = $1'
    else:
        squery += ' AND users.username = $1'
    query = await conn.fetchrow(squery, login)
    if query:
        return {'id': query.get('id'),
                'username': query.get('username'),
                'registered': query.get('registered'),
                'password_hash': query.get('password_hash'),
                'permissions': query.get('permissions'),
                'ava_hash': query.get('ava_hash')}
