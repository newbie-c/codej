from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, RedirectResponse

from ..auth.common import checkcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed
from ..common.pg import get_conn
from ..drafts.attri import status
from .pg import check_last_pub, check_topic, select_pub


async def show_blogs(request):
    current_user = await checkcu(request)
    conn = await get_conn(request.app.config)
    if not (page := await parse_page(request)) or \
       not (last := await check_last_pub(
           conn, page,
           request.app.config.get('ARTS_PER_PAGE', cast=int, default=3))):
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    pagination = await select_pub(
        request, conn, page,
        request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'public/show-blogs.html',
        {'request': request,
         'current_user': current_user,
         'pagination': pagination,
         'flashed': await get_flashed(request)})


async def show_topic(request):
    slug = request.path_params.get('slug')
    current_user = await checkcu(request)
    if current_user:
        return RedirectResponse(
            request.url_for('arts:show-art', slug=slug), 302)
    conn = await get_conn(request.app.config)
    target = dict()
    await check_topic(request, conn, slug, target)
    await conn.close()
    if not target :
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    return request.app.jinja.TemplateResponse(
        'public/show-topic.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'current_user': current_user,
         'target': target or None})
