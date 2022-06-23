from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, RedirectResponse

from ..auth.attri import permissions
from ..auth.common import checkcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed, set_flashed
from ..common.pg import get_conn
from ..common.urls import get_next
from ..drafts.attri import status
from .pg import (
    check_art, check_last_arts, check_last_auth, check_rel,
    select_arts, select_auth)


async def show_banded(request):
    current_user = await checkcu(request)
    if current_user is None:
        await set_flashed(request, 'Требуется авторизация')
        return RedirectResponse(
            await get_next(request, request.app.url_path_for(
                'arts:lenta')), 302)
    return request.app.jinja.TemplateResponse(
        'arts/show-banded.html',
        {'request': request,
         'current_user': current_user,
         'flashed': await get_flashed(request)})


async def show_author(request):
    current_user = await checkcu(request)
    username = request.path_params.get('username')
    if current_user is None:
        await set_flashed(request, 'Требуется авторизация.')
        return RedirectResponse(
            await get_next(request, request.app.url_path_for(
                'arts:show-auth', username=username)), 302)
    conn = await get_conn(request.app.config)
    target = await conn.fetchrow(
        '''SELECT id, username, permissions, description, last_published
             FROM users WHERE username = $1''', username)
    if target is None or \
       (permissions.CREATE_ENTITY not in target['permissions'] and
        target['last_published'] is None) or \
       not (page := await parse_page(request)) or \
       not (last := await check_last_auth(
           conn, target, current_user, page,
           request.app.config.get('ARTS_PER_PAGE', cast=int, default=3))):
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    pagination = await select_auth(
        request, conn, target, current_user, page,
        request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'arts/show-author.html',
        {'request': request,
         'current_user': current_user,
         'pagination': pagination,
         'author': target,
         'status': status,
         'flashed': await get_flashed(request)})


async def show_arts(request):
    current_user = await checkcu(request)
    if current_user is None:
        await set_flashed(request, 'Требуется авторизация.')
        return RedirectResponse(
            await get_next(request, request.app.url_path_for(
                'arts:show-arts')), 302)
    conn = await get_conn(request.app.config)
    if not (page := await parse_page(request)) or \
       not (last := await check_last_arts(
           conn, current_user, page,
           request.app.config.get('ARTS_PER_PAGE', cast=int, default=3))):
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    pagination = await select_arts(
        request, conn, current_user, page,
        request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'arts/show-arts.html',
        {'request': request,
         'current_user': current_user,
         'pagination': pagination,
         'status': status,
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
    if target is None:
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    rel = None
    if current_user['id'] != target['author_id']:
        rel = await check_rel(conn, current_user['id'], target['author_id'])
    await conn.close()
    print(target)
    return request.app.jinja.TemplateResponse(
        'arts/show-art.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'current_user': current_user,
         'status': status,
         'rel': rel,
         'target': target})
