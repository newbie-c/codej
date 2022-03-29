from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, RedirectResponse

from ..auth.attri import permissions
from ..auth.common import get_current_user
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed, set_flashed
from ..common.pg import get_conn
from ..common.urls import get_next
from .attri import status


async def show_albums(request):
    conn = await get_conn(request.app.config)
    current_user = await get_current_user(request, conn)
    if current_user is None:
        await conn.close()
        await set_flashed(request, 'Требуется авторизация.')
        return RedirectResponse(
            await get_next(
                request, request.app.url_path_for('pictures:show-albums')),
            302)
    if permissions.UPLOAD_PICTURES not in current_user['permissions']:
        await conn.close()
        raise HTTPException(status_code=403, detail='Доступ ограничен.')
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'pictures/show-albums.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'pagination': None,
         'status': status,
         'current_user': current_user})
