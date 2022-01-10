import asyncpg

from starlette.responses import JSONResponse
from starlette_wtf import csrf_protect

from ..common.flashed import get_flashed, set_flashed
from .forms import LoginForm
from .redi import assign_cache

captchaq = 'SELECT val, suffix FROM captchas ORDER BY random() LIMIT 1'


@csrf_protect
async def login(request):
    conn = await asyncpg.connect(request.app.config.get('DB'))
    form = await LoginForm.from_formdata(request)
    captcha = await conn.fetchrow(captchaq)

    form.suffix.data = await assign_cache(
        request.app.config.get('REDI'), 'captcha:',
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
    conn = await asyncpg.connect(request.app.config.get('DB'))
    captcha = await conn.fetchrow(captchaq)
    res = {'cache': await assign_cache(
        request.app.config.get('REDI'), 'captcha:',
        captcha.get('suffix'), captcha.get('val'), 180),
           'picture': request.url_for(
               'captcha:captcha', suffix=captcha.get('suffix'))}
    await conn.close()
    return JSONResponse(res)
