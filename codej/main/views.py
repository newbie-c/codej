import os

from starlette.responses import FileResponse, PlainTextResponse

from ..auth.common import get_current_user
from ..common.flashed import get_flashed
from ..common.pg import get_conn

robots = """User-agent: *
Disallow: /
"""


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
