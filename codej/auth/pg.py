from datetime import datetime, timedelta
from hashlib import md5

from passlib.hash import pbkdf2_sha256
from validate_email import validate_email

from .attri import permissions


async def check_account(config, conn, account, address):
    length = timedelta(
        seconds=round(3600*config.get('TOKEN_LENGTH', cast=float)))
    interval = timedelta(
        seconds=round(3600*config.get('REQUEST_INTERVAL', cast=float)))
    if datetime.utcnow() - account.get('requested') < interval:
        return 'Сервис временно недоступен, попробуйте зайти позже.'
    if account.get('address') == address:
        return 'Задан Ваш текущий адрес, запрос не имеет смысла.'
    if await check_swap(conn, address, length):
        return 'Адрес в свопе, выберите другой или повторите попытку позже.'
    requested = await conn.fetchrow(
        'SELECT requested, user_id FROM accounts WHERE address = $1', address)
    if requested and requested.get('user_id'):
        return 'Этот адрес уже зарегистрирован, запрос отклонён.'
    if requested and datetime.utcnow() - requested.get('requested') < length:
        return 'Адрес регистрируется, выберите другой или попробуйте позже.'
    return None


async def filter_acc(conn, username):
    return await conn.fetchrow(
        '''SELECT users.username, accounts.id, accounts.address,
                  accounts.swap, accounts.requested
             FROM users, accounts WHERE users.id = accounts.user_id
               AND users.username = $1''', username)


async def check_pwd(conn, username, password):
    if pbkdf2_sha256.verify(
            password,
            await conn.fetchval(
                'SELECT password_hash FROM users WHERE username = $1',
                username)):
        return True
    return False


async def change_pwd(conn, username, password):
    await conn.execute(
        '''UPDATE users SET password_hash = $1, last_visit = $2
             WHERE username = $3''',
        pbkdf2_sha256.hash(password), datetime.utcnow(), username)


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
                       users.permissions AS permissions,
                       users.registered AS registered,
                       accounts.ava_hash AS ava
                  FROM users, accounts WHERE users.id = accounts.user_id'''
    if validate_email(login):
        squery += ' AND accounts.address = $1'
    else:
        squery += ' AND users.username = $1'
    query = await conn.fetchrow(squery, login)
    if query and permissions.CANNOT_LOG_IN not in query.get('permissions'):
        return {'id': query.get('id'),
                'username': query.get('username'),
                'password_hash': query.get('password_hash'),
                'registered': query.get('registered'),
                'permissions': query.get('permissions'),
                'ava': query.get('ava')}
