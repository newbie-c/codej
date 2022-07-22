import asyncio
import functools

from datetime import datetime

from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, RedirectResponse

from ..auth.attri import permissions
from ..auth.common import checkcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed, set_flashed
from ..common.pg import get_conn
from ..common.urls import get_next
from ..labels.pg import select_labels
from .attri import status
from .md import parse_md
from .pg import (
    prepend_par, change_par, check_article, create_d,
    check_last_drafts, check_last_labeled, check_slug, remove_this,
    save_par, select_drafts, select_labeled_drafts)

spar = '''SELECT par.num, par.article_id, par.mdtext
            FROM paragraphs AS par, articles AS arts
              WHERE par.num = $1
                AND par.article_id = $2
                AND arts.author_id = $3
                AND par.article_id = arts.id'''


async def change_commented(request):
    res = {'empty': True}
    id = int((await request.form()).get('id'))
    current_user = await checkcu(request)
    if current_user and \
            permissions.CREATE_ENTITY in current_user['permissions']:
        conn = await get_conn(request.app.config)
        query = await conn.fetchrow(
            '''SELECT id, commented, author_id FROM articles
                 WHERE id = $1 AND author_id = $2''',
            id, current_user['id'])
        if query:
            await conn.execute(
                'UPDATE articles SET commented = $1 WHERE id = $2',
                not query.get('commented'), query.get('id'))
            res = {'empty': False}
            if query.get('commented'):
                message = 'Комментарии закрыты.'
            else:
                message = 'Комментарии открыты.'
            await set_flashed(request, message)
        await conn.close()
    return JSONResponse(res)


async def edit_state(request):
    res = {'empty': True}
    d = await request.form()
    art, state = int(d.get('art')), d.get('state')
    current_user = await checkcu(request)
    if state and state in status and current_user and \
            permissions.CREATE_ENTITY in current_user['permissions']:
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            '''SELECT id, state, published FROM articles
                 WHERE id = $1 AND author_id = $2''', art, current_user['id'])
        if target:
            if target.get('published') is None and \
                    state in (status.pub, status.priv, status.hidden):
                now = datetime.utcnow()
                await conn.execute(
                    '''UPDATE articles SET state = $1, published = $2
                         WHERE id = $3 AND author_id = $4''',
                    state, now, art, current_user['id'])
                await conn.execute(
                    'UPDATE users SET last_published = $1 WHERE id = $2',
                    now, current_user['id'])
            else:
                await conn.execute(
                    '''UPDATE articles SET state = $1
                         WHERE id = $2 AND author_id = $3''',
                    state, art, current_user['id'])
            res = {'empty': False}
        await conn.close()
    return JSONResponse(res)


async def edit_sum(request):
    res = {'empty': True}
    d = await request.form()
    art, s = int(d.get('art')), d.get('summary')
    current_user = await checkcu(request)
    if s and len(s) <= 512 and current_user and \
            permissions.CREATE_ENTITY in current_user['permissions']:
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            '''SELECT id, summary FROM articles
                 WHERE id = $1 AND author_id = $2''', art, current_user['id'])
        if target and s != target.get('summary'):
            await conn.execute(
                'UPDATE articles SET summary = $1 WHERE id = $2', s, art)
            res = {'empty': False}
        await conn.close()
    return JSONResponse(res)


async def edit_meta(request):
    res = {'empty': True}
    d = await request.form();
    art, meta = int(d.get('art')), d.get('meta')
    current_user = await checkcu(request)
    if meta and current_user and \
            permissions.CREATE_ENTITY in current_user['permissions']:
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            'SELECT id, meta FROM articles WHERE id = $1 AND author_id = $2',
            art, current_user['id'])
        if target and meta != target.get('meta') and len(meta) <= 180:
            await conn.execute(
                'UPDATE articles SET meta = $1 WHERE id = $2',
                meta, art)
            res = {'empty': False}
        await conn.close()
    return JSONResponse(res);


async def change_title(request):
    res = {'empty': True}
    d = await request.form()
    art, title = int(d.get('art')), d.get('title')
    current_user = await checkcu(request)
    if title and len(title) <= 100 and current_user and \
            permissions.CREATE_ENTITY in current_user['permissions']:
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            '''SELECT id, title, slug FROM articles
                 WHERE id = $1 AND author_id = $2''',
            art, current_user['id'])
        if target and title != target.get('title'):
            slug = await check_slug(conn, title)
            await conn.execute(
                '''UPDATE articles SET title = $1, slug = $2
                     WHERE id = $3''', title, slug, art)
            res = {'empty': False,
                   'url': request.url_for('drafts:show-draft', slug=slug)}
        await conn.close()
    return JSONResponse(res)


async def insert_par(request):
    res = {'empty': True}
    d = await request.form()
    art, num, text, code = (
        int(d.get('art')), int(d.get('num')),
        d.get('text'), bool(int(d.get('code'))))
    current_user = await checkcu(request)
    if current_user and \
            permissions.CREATE_ENTITY in current_user['permissions']:
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(spar, num, art, current_user['id'])
        if target:
            res = {'empty': False,
                   'html': await prepend_par(conn, art, num, text, code)}
        await conn.close()
    return JSONResponse(res)


async def rem_par(request):
    res = {'empty': True}
    d = await request.form()
    art, num = int(d.get('art')), int(d.get('num'))
    current_user = await checkcu(request)
    if current_user and \
            permissions.CREATE_ENTITY in current_user['permissions']:
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(spar, num, art, current_user['id'])
        if target:
            last = await remove_this(
                conn, target.get('article_id'), target.get('num'))
            res = {'empty': False}
            if not last:
                await set_flashed(request, 'Последний абзац нельзя удалить.')
        await conn.close()
    return JSONResponse(res)


async def edit_par(request):
    res = {'empty': True}
    d = await request.form()
    art, num, text, code = (
        int(d.get('art')), int(d.get('num')),
        d.get('text'), bool(int(d.get('code'))))
    current_user = await checkcu(request)
    if current_user and \
            permissions.CREATE_ENTITY in current_user['permissions']:
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            spar, num, art, current_user['id'])
        if target:
            res = {'empty': False,
                   'html': await change_par(conn, target, text, code)}
        await conn.close()
    return JSONResponse(res)


async def check_par(request):
    res = {'empty': True}
    d = await request.form()
    art, num = int(d.get('art')), int(d.get('num'))
    current_user = await checkcu(request)
    if current_user and \
            permissions.CREATE_ENTITY in current_user['permissions']:
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            spar, num, art, current_user['id'])
        if target:
            res = {'empty': False,
                   'html': request.app.jinja.get_template(
                       'drafts/check-par.html').render(
                       request=request, mdtext=target.get('mdtext'),
                       num=num, art=art)}
        await conn.close()
    return JSONResponse(res)


async def rem_rel(request):
    res = {'empty': True}
    id = int((await request.form()).get('id'))
    current_user = await checkcu(request)
    if current_user and \
            permissions.SPECIAL_CASE in current_user['permissions']:
        conn = await get_conn(request.app.config)
        query = await conn.fetchrow(
            '''SELECT id, author_id FROM articles
                 WHERE id = $1 AND author_id = $2''', id, current_user['id'])
        if query:
            pars = await conn.fetch(
                '''SELECT mdtext FROM paragraphs
                     WHERE article_id = $1 ORDER BY num ASC''',
                query.get('id'))
            loop = asyncio.get_running_loop()
            html = await loop.run_in_executor(
                None, functools.partial(parse_md, pars, True))
            await conn.execute(
                'UPDATE articles SET html = $1 WHERE id = $2',
                html, query.get('id'))
            await set_flashed(request, 'Аттрибут удалён.')
            res = {'empty': False}
        await conn.close()
    return JSONResponse(res)


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
    await conn.close()
    return JSONResponse(res)


async def show_draft(request):
    current_user = await checkcu(request)
    slug = request.path_params.get('slug')
    if current_user is None:
        await set_flashed(request, 'Требуется авторизация.')
        return RedirectResponse(
            await get_next(request, request.app.url_path_for(
                'drafts:show-draft', slug=slug)), 302)
    slug = request.path_params.get('slug')
    conn = await get_conn(request.app.config)
    target = dict()
    await check_article(request, conn, slug, current_user['id'], target)
    if not target:
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    length = await conn.fetchval(
        'SELECT count(*) FROM paragraphs WHERE article_id = $1', target['id'])
    labels = await select_labels(conn, target['id'])
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'drafts/draft.html',
        {'request': request,
         'current_user': current_user,
         'status': status,
         'length': length,
         'labels': labels or None,
         'flashed': await get_flashed(request),
         'target': target or None})


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


async def show_labeled(request):
    label = request.path_params.get('label')
    current_user = await checkcu(request)
    if current_user is None:
        await set_flashed(request, 'Требуется авторизация.')
        return RedirectResponse(
            await get_next(request, request.app.url_path_for(
                'drafts:show-labeled', label=label)), 302)
    conn = await get_conn(request.app.config)
    if not (page := await parse_page(request)) or \
       not (last := await check_last_labeled(
           conn, current_user['id'], label, page,
           request.app.config.get('ARTS_PER_PAGE', cast=int, default=3))):
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    pagination = dict()
    await select_labeled_drafts(
        request, conn, current_user['id'], label, pagination, page,
        request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'drafts/labeled.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'label': label,
         'status': status,
         'current_user': current_user,
         'pagination': pagination or None})


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
    pagination = dict()
    await select_drafts(
        request, conn, current_user['id'], pagination, page,
        request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'drafts/drafts.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'pagination': pagination or None,
         'status': status,
         'current_user': current_user})
