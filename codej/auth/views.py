import asyncio

from passlib.hash import pbkdf2_sha256
from starlette.exceptions import HTTPException
from starlette.responses import (
        PlainTextResponse, JSONResponse, RedirectResponse)
from starlette_wtf import csrf_protect

from ..common.flashed import get_flashed, set_flashed
from ..common.pg import get_conn
from .common import get_current_user
from .forms import CreatePassword, GetPassword, LoginForm
from .pg import check_address, create_user, filter_user
from .redi import assign_cache, assign_uid, extract_cache
from .tasks import (
    change_pattern, rem_old_session, rem_user_session, request_password)
from .tokens import check_token

captchaq = 'SELECT val, suffix FROM captchas ORDER BY random() LIMIT 1'


@csrf_protect
async def create_password(request):
    conn = await get_conn(request.app.config)
    current_user = await get_current_user(request, conn)
    acc = await check_token(request, conn)
    if acc is None or current_user or acc.get('user_id'):
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    form = await CreatePassword.from_formdata(request)
    if await form.validate_on_submit():
        if await conn.fetchval(
                'SELECT username FROM users WHERE username = $1',
                form.username.data):
            await set_flashed(
                request, f'Псевдоним "{form.username.data}" уже занят.')
            await conn.close()
            return RedirectResponse(
                request.url_for('auth:create-password',
                    token=request.path_params['token']), 302)
        await create_user(
            conn, form.username.data, form.password.data, acc.get('address'))
        await set_flashed(request, 'Ваш аккаунт успешно зарегистрирован.')
        await conn.close()
        return RedirectResponse(request.url_for('auth:login'), 302)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'auth/create-password.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'form': form,
         'interval': request.app.config.get('REQUEST_INTERVAL', cast=float)})


async def reset_password(request):
    return PlainTextResponse('Страница сброса забытого пароля')


@csrf_protect
async def get_password(request):
    conn = await get_conn(request.app.config)
    if await get_current_user(request, conn):
        await set_flashed(request, 'У Вас уже есть пароль.')
        await conn.close()
        return RedirectResponse(request.url_for('index'), 302)
    captcha = await conn.fetchrow(captchaq)
    form = await GetPassword.from_formdata(request)
    if await form.validate_on_submit():
        suffix, val = await extract_cache(
            request.app.rc, form.suffix.data)
        if val != form.captcha.data:
            await set_flashed(
                request, 'Тест провален, либо устарел, попробуйте снова.')
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            await conn.close()
            return RedirectResponse(request.url_for('auth:get-password'), 302)
        message, account = await check_address(
            request, conn, form.address.data)
        if message:
            await set_flashed(request, message)
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            await conn.close()
            return RedirectResponse(
                request.url_for('auth:get-password'), 302)
        asyncio.ensure_future(
            request_password(request, account, form.address.data))
        asyncio.ensure_future(
            change_pattern(request.app.config, suffix))
        await set_flashed(
            request, 'На ваш адрес выслано письмо с инструкциями.')
        await conn.close()
        return RedirectResponse(request.url_for('index'), 302)
    form.captcha.data = ''
    form.suffix.data = await assign_cache(
        request.app.rc, 'captcha:',
        captcha.get('suffix'), captcha.get('val'), 180)
    return request.app.jinja.TemplateResponse(
        'auth/get-password.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'form': form,
         'captcha': captcha})


@csrf_protect
async def login(request):
    conn = await get_conn(request.app.config)
    if await get_current_user(request, conn):
        await set_flashed(request, 'Вы уже авторизованы!')
        await conn.close()
        return RedirectResponse(request.url_for('index'), 302)
    form = await LoginForm.from_formdata(request)
    captcha = await conn.fetchrow(captchaq)
    if await form.validate_on_submit():
        suffix, val = await extract_cache(
            request.app.rc, form.suffix.data)
        if val != form.captcha.data:
            await set_flashed(
                request, 'Тест провален, либо устарел, попробуйте снова.')
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            await conn.close()
            return RedirectResponse(request.url_for('auth:login'), 302)
        user = await filter_user(conn, form.login.data)
        if user and pbkdf2_sha256.verify(
                form.password.data, user.get('password_hash')):
            request.session['_uid'] = await assign_uid(
                request.app.rc, 'uid:',
                form.remember_me.data, user)
            await set_flashed(request, f'Привет {user.get("username")}!')
            if form.remember_me.data:
                asyncio.ensure_future(
                    rem_old_session(
                        request, request.session['_uid'], user['username']))
            asyncio.ensure_future(
                change_pattern(request.app.config, suffix))
            await conn.close()
            return RedirectResponse(
                request.url_for('auth:fake-index'), 302)
        await set_flashed(
            request, 'Неверный логин или пароль, вход невозможен.')
        await conn.close()
        return RedirectResponse(
            request.url_for('auth:login'), 302)
    form.suffix.data = await assign_cache(
        request.app.rc, 'captcha:',
        captcha.get('suffix'), captcha.get('val'), 180)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'auth/login.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'form': form,
         'captcha': captcha})


async def logout(request):
    conn = await get_conn(request.app.config)
    current_user = await get_current_user(request, conn)
    response = RedirectResponse(request.url_for('index'), 302)
    if current_user is None:
        await conn.close()
        return response
    uid = request.session['_uid']
    if uid:
        await request.app.rc.delete(uid)
        del request.session['_uid']
        asyncio.ensure_future(
            rem_user_session(request, uid, current_user['username']))
    await set_flashed(request, f'Пока, {current_user.get("username")}')
    await conn.close()
    return response


@csrf_protect
async def update_captcha(request):
    conn = await get_conn(request.app.config)
    captcha = await conn.fetchrow(captchaq)
    res = {'cache': await assign_cache(
        request.app.rc, 'captcha:',
        captcha.get('suffix'), captcha.get('val'), 180),
           'picture': request.url_for(
               'captcha:captcha', suffix=captcha.get('suffix'))}
    await conn.close()
    return JSONResponse(res)


async def fake_index(request):
    conn = await get_conn(request.app.config)
    current_user = await get_current_user(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'main/index.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'target': None,
         'current_user': current_user})
