from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, RedirectResponse

from ..auth.common import checkcu
from ..auth.attri import permissions
from ..common.flashed import get_flashed, set_flashed
from ..common.pg import get_conn
from ..common.urls import get_next


async def show_drafts(request):
    current_user = await checkcu(request)
    if current_user is None:
        await set_flashed(request, 'Требуется авторизация.')
        return RedirectResponse(
            await get_next(request, request.app.url_path_for(
                'drafts:show-drafts')), 302)
    return request.app.jinja.TemplateResponse(
        'drafts/drafts.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'pagination': None,
         'current_user': current_user})
