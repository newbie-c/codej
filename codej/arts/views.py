from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, RedirectResponse

from ..auth.common import checkcu
from ..common.flashed import get_flashed, set_flashed
from ..common.pg import get_conn
from ..common.urls import get_next
from ..drafts.attri import status
from .pg import check_art


async def show_arts(request):
    current_user = await checkcu(request)
    return request.app.jinja.TemplateResponse(
        'arts/show-arts.html',
        {'request': request,
         'current_user': current_user,
         'flashed': await get_flashed(request)})


async def show_art(request):
    slug = request.path_params.get('slug')
    current_user = await checkcu(request)
    if current_user is None:
        await set_flashed(request, 'Требуется авторизация.')
        url = await get_next(
            request, request.app.url_path_for('arts:show-art', slug=slug))
        return RedirectResponse(url, 302)
    conn = await get_conn(request.app.config)
    target = await check_art(request, conn, slug)
    await conn.close()
    if target is None:
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    return request.app.jinja.TemplateResponse(
        'arts/show-art.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'current_user': current_user,
         'status': status,
         'target': target})
