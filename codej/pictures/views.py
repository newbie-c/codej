from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, RedirectResponse

from ..auth.attri import permissions
from ..auth.common import get_current_user
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed, set_flashed
from ..common.pg import get_conn
from ..common.urls import get_next
from .attri import status
from .pg import (
    check_last_albums, create_new_album, get_user_stat, select_albums)


async def show_album(request):
    return JSONResponse({'empty': 'yes'})


async def create_album(request):
    res = {'empty': True}
    d = await request.form()
    if d.get('title') and d.get('state'):
        conn = await get_conn(request.app.config)
        current_user = await get_current_user(request, conn)
        if permissions.UPLOAD_PICTURES in current_user['permissions']:
            rep = await conn.fetchval(
                '''SELECT suffix FROM albums
                     WHERE title = $1 AND author_id = $2''',
                d.get('title').strip(), current_user['id'])
            if rep:
                res = {'empty': False,
                       'redirect': request.url_for(
                           'pictures:show-album', suffix=rep)}
            else:
                new = await create_new_album(
                    conn, current_user['id'],
                    d.get('title').strip(), d.get('state').strip())
                res = {'empty': False,
                       'redirect': request.url_for(
                           'pictures:show-album', suffix=new)}
        await conn.close()
    return JSONResponse(res)


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
    if not (page := await parse_page(request)) or \
       not (last := await check_last_albums(
           conn, current_user['id'], page,
           request.app.config.get('ALBUMS_PER_PAGE', cast=int, default=3))):
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    pagination = await select_albums(
        conn, current_user['id'], page,
        request.app.config.get('ALBUMS_PER_PAGE', cast=int, default=3), last)
    stat = await get_user_stat(conn, current_user['id'])
    print(stat)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'pictures/show-albums.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'pagination': pagination,
         'status': status,
         'stat': stat,
         'current_user': current_user})
