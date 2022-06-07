from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, RedirectResponse

from ..auth.common import checkcu
from ..common.flashed import get_flashed
from ..common.pg import get_conn
from ..drafts.attri import status
from .pg import check_topic


async def show_topic(request):
    slug = request.path_params.get('slug')
    current_user = await checkcu(request)
    print(current_user)
    if current_user:
        return RedirectResponse(
            request.url_for('arts:show-art', slug=slug), 302)
    conn = await get_conn(request.app.config)
    target = await check_topic(request, conn, slug)
    if target is None:
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'public/show-topic.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'current_user': current_user,
         'target': target})
