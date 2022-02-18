import os

from starlette.exceptions import HTTPException
from starlette.responses import (
    FileResponse, PlainTextResponse, RedirectResponse)

from ..auth.common import get_current_user
from ..common.flashed import get_flashed, set_flashed
from ..common.pg import get_conn
from ..common.urls import get_next
from .pg import filter_target_user

robots = """User-agent: *
Disallow: /
"""


async def show_profile(request):
    conn = await get_conn(request.app.config)
    current_user = await get_current_user(request, conn)
    if current_user is None:
        await set_flashed(request, 'Требуется авторизация.')
        await conn.close()
        return RedirectResponse(
            await get_next(request, request.app.url_path_for(
                'profile', username=request.path_params['username'])), 302)
    target = await filter_target_user(request, conn)
    if target is None:
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'main/profile.html',
        {'request': request,
         'current_user': current_user,
         'target': target,
         'flashed': await get_flashed(request)})


async def show_index(request):
    conn = await get_conn(request.app.config)
    current_user = await get_current_user(request, conn)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'main/index.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'target': None,
         'current_user': current_user})


async def show_robots(request):
    if request.method == 'GET':
        return PlainTextResponse(robots)


async def show_favicon(request):
    if request.method == 'GET':
        base = os.path.dirname(os.path.dirname(__file__))
        return FileResponse(
            os.path.join(base, 'static', 'images', 'favicon.ico'))
