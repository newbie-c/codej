from datetime import datetime, timedelta
from hashlib import md5

from passlib.hash import pbkdf2_sha256
from validate_email import validate_email

from .attri import permissions


async def create_user(conn, username, password, address):
    now = datetime.utcnow()
    perms = await conn.fetch(
        'SELECT permission FROM permissions WHERE init = true')
    await conn.execute(
        '''INSERT INTO users
             (username, registered, last_visit, password_hash, permissions)
             VALUES ($1, $2, $3, $4, $5)''',
        username, now, now,
        pbkdf2_sha256.hash(password),
        [each.get('permission') for each in perms])
    user_id = await conn.fetchval(
        'SELECT id FROM users WHERE username = $1', username)
    await conn.execute(
        'UPDATE accounts SET user_id = $1 WHERE address = $2',
        user_id, address)


async def define_a(conn, account):
    if account and account.get('user_id'):
        username = await conn.fetchval(
            'SELECT username FROM users WHERE id = $1', account.get('user_id'))
        return username, 'Сброс забытого пароля', 'emails/resetpwd.html'
    return 'Гость', 'Регистрация', 'emails/invitation.html'


async def get_acc(conn, account, address):
    now = datetime.utcnow()
    if account:
        address = account.get('address')
        await conn.execute(
            '''UPDATE accounts SET swap = null, requested = $1
                 WHERE address = $2''',
            now, address)
    else:
        await conn.execute(
            '''INSERT INTO accounts (address, ava_hash, requested)
                 VALUES ($1, $2, $3)''',
            address, md5(address.encode('utf-8')).hexdigest(), now)
    return await conn.fetchrow(
        'SELECT id, address, user_id FROM accounts WHERE address = $1',
        address)


async def check_swap(conn, address, length):
    swapped = await conn.fetchrow(
        'SELECT id, swap, requested FROM accounts WHERE swap = $1', address)
    if swapped:
        if datetime.utcnow() - swapped.get('requested') > length:
            await conn.execute(
                'UPDATE accounts SET swap = null WHERE id = $1',
                swapped.get('id'))
            return None
        else:
            return True


async def check_address(request, conn, address):
    message = None
    interval = timedelta(
        seconds = round(
            3600*request.app.config.get('REQUEST_INTERVAL', cast=float)))
    length = timedelta(
        seconds = round(
            3600*request.app.config.get('TOKEN_LENGTH', cast=float)))
    acc = await conn.fetchrow(
        'SELECT address, requested, user_id FROM accounts WHERE address = $1',
        address)
    if acc and datetime.utcnow() - acc.get('requested') < interval:
        message = 'Сервис временно недоступен, попробуйте зайти позже.'
    if await check_swap(conn, address, length):
        message = 'Адрес в свопе, выберите другой или повторите попытку позже.'
    return message, acc


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
