from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, RedirectResponse

from ..auth.attri import permissions
from ..auth.common import checkcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed, set_flashed
from ..common.pg import get_conn
from ..common.urls import get_next
from .attri import status
from .pg import (
    check_article, create_d, check_last_drafts, save_par, select_drafts)


async def create_par(request):
    res = {'empty': True}
    d = await request.form()
    art, text, code = (
        int(d.get('art')), d.get('text'), bool(int(d.get('code'))))
    conn = await get_conn(request.app.config)
    target = await conn.fetchrow(
        '''SELECT id, html, author_id FROM articles WHERE id = $1''',
        art)
    current_user = await checkcu(request)
    if text and target and current_user['id'] == target['author_id'] and \
            permissions.CREATE_ENTITY in current_user['permissions']:
        html = await save_par(conn, art, text, code)
        res = {'empty': False, 'html': html}
    return JSONResponse(res)


async def show_draft(request):
    current_user = await checkcu(request)
    slug = request.path_params.get('slug')
    conn = await get_conn(request.app.config)
    target = await check_article(request, conn, slug)
    if target is None:
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    if current_user is None:
        await conn.close()
        await set_flashed(request, 'Требуется авторизация.')
        return RedirectResponse(
            await get_next(request, request.app.url_path_for(
                'drafts:show-draft', slug=slug)), 302)
    if target.get('author_id') != current_user['id'] or \
            permissions.CREATE_ENTITY not in current_user['permissions']:
        await conn.close()
        raise HTTPException(
            status_code=403, detail='Для вас доступ ограничен.')
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'drafts/draft.html',
        {'request': request,
         'current_user': current_user,
         'status': status,
         'flashed': await get_flashed(request),
         'target': target})


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
    conn = await get_conn(request.app.config)
    if not (page := await parse_page(request)) or \
       not (last := await check_last_drafts(
           conn, current_user['id'], page,
           request.app.config.get('ARTS_PER_PAGE', cast=int, default=3))):
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    pagination = await select_drafts(
        request, conn, current_user['id'], page,
        request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'drafts/drafts.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'pagination': pagination,
         'status': status,
         'current_user': current_user})
