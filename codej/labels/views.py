import re

from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, RedirectResponse

from ..auth.attri import permissions
from ..auth.common import checkcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed, set_flashed
from ..common.pg import get_conn
from ..common.urls import get_next
from .pg import check_last, select_found, select_labels, select_ls


async def find_label(request):
    res = {'empty': True}
    value = (await request.form()).get('value')
    current_user = await checkcu(request)
    if value and current_user:
        conn = await get_conn(request.app.config)
        pagination = dict()
        await select_found(conn, pagination, value)
        res = {'empty': False,
               'html': request.app.jinja.get_template(
                   'labels/found.html').render(
                   current_user=current_user, pagination=pagination,
                   request=request)}
        await conn.close()
    return JSONResponse(res)


async def show_labels(request):
    current_user = await checkcu(request)
    if current_user is None:
        await set_flashed(request, 'Требуется авторизация.')
        return RedirectResponse(
            await get_next(request, request.app.url_path_for(
                'labels:show')), 302)
    conn = await get_conn(request.app.config)
    if not (page := await parse_page(request)) or \
       not (last := await check_last(
           conn, page,
           request.app.config.get('LABELS_PER_PAGE', cast=int, default=3))):
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    pagination = dict()
    await select_ls(
        conn, pagination, page,
        request.app.config.get('LABELS_PER_PAGE', cast=int, default=3), last)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'labels/show.html',
        {'request': request,
         'current_user': current_user,
         'pagination': pagination or None,
         'flashed': await get_flashed(request)})


async def set_labels(request):
    res = {'empty': True}
    d = await request.form()
    aid, labels = int(d.get('aid')), d.get('labels')
    current_user = await checkcu(request)
    if aid and current_user and \
            permissions.CREATE_ENTITY in current_user['permissions']:
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            '''SELECT id, author_id FROM articles
                 WHERE id = $1 AND author_id = $2''', aid, current_user['id'])
        if target:
            current = await select_labels(conn, aid)
            new = [l.strip().lower() for l in labels.split(',') if l]
            for each in new:
                if not re.match(r'^[a-zа-яё\d\-]{1,32}$', each):
                    res = {'empty': False, 'error': True}
                    await conn.close()
                    return JSONResponse(res)
            lq = 'SELECT id FROM labels WHERE label = $1'
            for each in current:
                if each not in new:
                    lid = await conn.fetchval(lq, each)
                    await conn.execute(
                        '''DELETE FROM als
                             WHERE article_id = $1 AND label_id = $2''',
                        aid, lid)
            for each in new:
                if each not in current:
                    lid = await conn.fetchval(lq, each)
                    if lid is None:
                        await conn.execute(
                            'INSERT INTO labels (label) VALUES ($1)', each)
                        lid = await conn.fetchval(lq, each)
                    await conn.execute(
                        '''INSERT INTO als (article_id, label_id)
                             VALUES ($1, $2)''', aid, lid)
            res = {'empty': False, 'error': False}
            await set_flashed(request, 'Метки установлены.')
        await conn.close()
    return JSONResponse(res)
