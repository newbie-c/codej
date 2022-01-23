import asyncio

from passlib.hash import pbkdf2_sha256
from starlette.responses import JSONResponse, RedirectResponse
from starlette_wtf import csrf_protect

from ..common.flashed import get_flashed, set_flashed
from ..common.pg import get_conn
from .common import get_current_user
from .forms import LoginForm
from .pg import filter_user
from .redi import assign_cache, assign_uid, extract_cache
from .tasks import change_pattern, rem_old_session

captchaq = 'SELECT val, suffix FROM captchas ORDER BY random() LIMIT 1'


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
                request.url_for('index'), 302)
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
