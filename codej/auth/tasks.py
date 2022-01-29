import asyncio
import functools

from aiosmtplib import send
from email.message import EmailMessage

from ..common.pg import get_conn
from ..captcha.common import check_val
from ..captcha.picturize.picture import generate_image
from .pg import define_a, get_acc
from .tokens import get_request_token
from .tools import define_target_url


async def request_password(request, account, address):
    conn = await get_conn(request.app.config)
    username, subject, template = await define_a(conn, account)
    account = await get_acc(conn, account, address)
    url = await define_target_url(
        request, account,
        await get_request_token(request, account.get('id')))
    content = request.app.jinja.get_template(template).render(
        username=username, index=request.url_for('index'),
        target=url, length=request.app.config.get('TOKEN_LENGTH', cast=float),
        interval=request.app.config.get('REQUEST_INTERVAL', cast=float))
    if request.app.config.get('DEBUG', cast=bool):
        print(content)
    else:
        message = EmailMessage()
        message["From"] = request.app.config.get('SENDER', cast=str)
        message["To"] = account.get('address')
        message["Subject"] = request.app.config.get(
            'SUBJECT_PREFIX', cast=str) + subject
        message.set_content(content)
        message.replace_header('Content-Type', 'text/html; charset="utf-8"')
        await send(
            message,
            recipients=[account.get('address')],
            hostname=request.app.config.get('MAIL_SERVER', cast=str),
            port=request.app.config.get('MAIL_PORT', cast=str),
            username=request.app.config.get('MAIL_USERNAME', cast=str),
            password=request.app.config.get('MAIL_PASSWORD', cast=str),
            use_tls=request.app.config.get('MAIL_USE_SSL', cast=bool))
    await conn.close()
    return None


async def rem_user_session(request, session, username):
    conn = await get_conn(request.app.config)
    sessions = await conn.fetchval(
        'SELECT sessions FROM users WHERE username = $1', username)
    if sessions and session in sessions:
        sessions.remove(session)
        await conn.execute(
            'UPDATE users SET sessions = $1 WHERE username = $2',
            sessions or None, username)
    await conn.close()
    return None


async def ping_user(request, timestamp, uid):
    conn = await get_conn(request.app.config)
    await conn.execute(
        'UPDATE users SET last_visit = $1 WHERE id = $2', timestamp, uid)
    await conn.close()


async def rem_old_session(request, uid_, username):
    conn = await get_conn(request.app.config)
    sessions = await conn.fetchval(
        'SELECT sessions FROM users WHERE username = $1', username) or list()
    sessions.append(uid_)
    if len(sessions) > 3:
        old = sessions[0]
        if await request.app.rc.exists(old):
            await request.app.rc.delete(old)
        del sessions[0]
    await conn.execute(
        'UPDATE users SET sessions = $1 WHERE username = $2',
        sessions, username)
    await conn.close()


async def change_pattern(conf, suffix):
    conn = await get_conn(conf)
    val = await check_val(conn)
    loop = asyncio.get_running_loop()
    pic = await loop.run_in_executor(
        None, functools.partial(generate_image, val))
    await conn.execute(
        'UPDATE captchas SET val = $1, picture = $2 WHERE suffix = $3',
        val, pic.read(), suffix)
    pic.close()
    await conn.close()
    return None
