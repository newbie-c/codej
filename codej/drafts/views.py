from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, RedirectResponse

from ..auth.common import checkcu
from ..auth.attri import permissions
from ..common.flashed import get_flashed, set_flashed
from ..common.pg import get_conn
from ..common.urls import get_next
from .pg import create_d


async def show_draft(request):
    slug = request.path_params.get('slug')
    return JSONResponse({'slug': slug})


async def create_draft(request):
    res = {'empty': True}
    title = (await request.form()).get('title')
    if title:
        title = title.strip()
    current_user = await checkcu(request)
    if title and len(title) <= 100 and current_user and \
            permissions.CREATE_ENTITY in current_user['permissions']:
        conn = await get_conn(request.app.config)
        slug = await create_d(conn, title, current_user['id'])
        res = {'empty': False,
               'url': request.url_for('drafts:show-draft', slug=slug)}
        await conn.close()
    return JSONResponse(res)


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
