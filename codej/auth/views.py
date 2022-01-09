import asyncpg

from starlette_wtf import csrf_protect

from ..common.flashed import get_flashed, set_flashed
from .forms import LoginForm


@csrf_protect
async def login(request):
    conn = await asyncpg.connect(request.app.config.get('DB'))
    form = await LoginForm.from_formdata(request)
    captcha = await conn.fetchrow(
        'SELECT val, suffix FROM captchas ORDER BY random() LIMIT 1')
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'auth/login.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'form': form,
         'captcha': captcha})
