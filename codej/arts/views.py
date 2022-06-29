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
    check_art, check_last_arts, check_last_auth, check_last_banded,
    check_last_blocked, check_rel, select_arts, select_auth,
    select_banded, select_blocked)


async def censor_art(request):
    res = {'empty': True}
    suffix = (await request.form()).get('suffix')
    current_user = await checkcu(request)
    if suffix and current_user and \
            permissions.BLOCK_ENTITY in current_user['permissions']:
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            'SELECT id, state FROM articles WHERE suffix = $1', suffix)
        if target:
            if target.get('state') != status.mod:
                await conn.execute(
                    'UPDATE articles SET state = $1 WHERE id = $2',
                    status.mod, target.get('id'))
            else:
                await conn.execute(
                    'UPDATE articles SET state = $1 WHERE id = $2',
                    status.hidden, target.get('id'))
            res = {'empty': False}
        await conn.close()
    return JSONResponse(res)


async def send_dislike(request):
    res = {'empty': True}
    suffix = (await request.form()).get('suffix')
    current_user = await checkcu(request)
    if suffix and current_user and \
            permissions.LIKE_DISLIKE in current_user['permissions']:
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            '''SELECT id, suffix, author_id, state FROM articles
                 WHERE suffix = $1''', suffix)
        if target and target.get('author_id') != current_user['id'] and \
                target.get('state') in (
                        status.pub, status.priv, status.hidden):
            rel = await check_rel(
                conn, current_user['id'], target['author_id'])
            if not rel['blocker'] and not rel['blocked']:
                l = await conn.fetchrow(
                    '''SELECT * FROM art_likes
                         WHERE article_id = $1 AND user_id = $2''',
                    target.get('id'), current_user['id'])
                d = await conn.fetchrow(
                    '''SELECT * FROM art_dislikes
                         WHERE article_id = $1 AND user_id = $2''',
                    target.get('id'), current_user['id'])
                if l:
                    await conn.execute(
                        '''DELETE FROM art_likes
                             WHERE article_id = $1 AND user_id = $2''',
                        target.get('id'), current_user['id'])
                if not l and not d:
                    await conn.execute(
                        '''INSERT INTO art_dislikes (article_id, user_id)
                           VALUES ($1, $2)''',
                        target.get('id'), current_user['id'])
                res = {'empty': False,
                   'likes': await conn.fetchval(
                       'SELECT count(*) FROM art_likes WHERE article_id = $1',
                       target.get('id')),
                   'dislikes': await conn.fetchval(
                       '''SELECT count(*) FROM art_dislikes
                            WHERE article_id = $1''', target.get('id'))}
        await conn.close()
    return JSONResponse(res)


async def send_like(request):
    res = {'empty': True}
    suffix = (await request.form()).get('suffix')
    current_user = await checkcu(request)
    if suffix and current_user and \
            permissions.LIKE_DISLIKE in current_user['permissions']:
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            '''SELECT id, suffix, author_id, state FROM articles
                 WHERE suffix = $1''', suffix)
        if target and target.get('author_id') != current_user['id'] and \
                target.get('state') in (
                        status.pub, status.priv, status.hidden):
            l = await conn.fetchrow(
                '''SELECT * FROM art_likes
                     WHERE article_id = $1 AND user_id = $2''',
                target.get('id'), current_user['id'])
            d = await conn.fetchrow(
                '''SELECT * FROM art_dislikes
                     WHERE article_id = $1 AND user_id = $2''',
                target.get('id'), current_user['id'])
            if d:
                await conn.execute(
                    '''DELETE FROM art_dislikes
                         WHERE article_id = $1 AND user_id = $2''',
                    target.get('id'), current_user['id'])
            if not d and not l:
                await conn.execute(
                    '''INSERT INTO art_likes (article_id, user_id)
                       VALUES ($1, $2)''',
                    target.get('id'), current_user['id'])
            res = {'empty': False,
                   'likes': await conn.fetchval(
                       'SELECT count(*) FROM art_likes WHERE article_id = $1',
                       target.get('id')),
                   'dislikes': await conn.fetchval(
                       '''SELECT count(*) FROM art_dislikes
                            WHERE article_id = $1''', target.get('id'))}
        await conn.close()
    return JSONResponse(res)


async def unfollow_auth(request):
    res = {'empty': True}
    suffix = (await request.form()).get('suffix')
    current_user = await checkcu(request)
    if suffix and current_user and \
            permissions.FOLLOW_USERS in current_user['permissions']:
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            '''SELECT users.id, users.username FROM users, articles
                 WHERE articles.suffix = $1
                   AND users.id = articles.author_id''', suffix)
        if target:
            rel = await check_rel(conn, current_user['id'], target.get('id'))
            if rel['follower']:
                await conn.execute(
                    '''DELETE FROM followers
                       WHERE author_id = $1 AND follower_id = $2''',
                    target.get('id'), current_user['id'])
                res = {'empty': False}
                await set_flashed(
                    request,
                    f'Блог {target.get("username")} удалён из вашей ленты.')
        await conn.close()
    return JSONResponse(res)


async def follow_auth(request):
    res = {'empty': True}
    suffix = (await request.form()).get('suffix')
    current_user = await checkcu(request)
    if suffix and current_user and \
            permissions.FOLLOW_USERS in current_user['permissions']:
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            '''SELECT users.id, users.username FROM users, articles
                 WHERE articles.suffix = $1
                   AND users.id = articles.author_id''', suffix)
        if target:
            rel = await check_rel(conn, current_user['id'], target.get('id'))
            if not rel['follower'] and not rel['blocker'] \
                    and not rel['blocked']:
                await conn.execute(
                    '''INSERT INTO followers (author_id, follower_id)
                         VALUES ($1, $2)''',
                    target.get('id'), current_user['id'])
                res = {'empty': False}
                await set_flashed(
                    request,
                    f'Блог {target.get("username")} добавлен в вашу ленту.')
        await conn.close()
    return JSONResponse(res)


async def show_blocked(request):
    current_user = await checkcu(request)
    if current_user is None:
        await set_flashed(request, 'Требуется авторизация.')
        return RedirectResponse(
            await get_next(request, request.app.url_path_for(
                'arts:show-blocked')), 302)
    if permissions.BLOCK_ENTITY not in current_user['permissions']:
        raise HTTPException(
            status_code=403, detail='Для вас доступ ограничен.')
    conn = await get_conn(request.app.config)
    if not (page := await parse_page(request)) or \
       not (last := await check_last_blocked(
           conn, page,
           request.app.config.get('ARTS_PER_PAGE', cast=int, default=3))):
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    pagination = await select_blocked(
        request, conn, page,
        request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'arts/show-blocked.html',
        {'request': request,
         'current_user': current_user,
         'pagination': pagination,
         'status': status,
         'flashed': await get_flashed(request)})


async def show_banded(request):
    current_user = await checkcu(request)
    if current_user is None:
        await set_flashed(request, 'Требуется авторизация.')
        return RedirectResponse(
            await get_next(request, request.app.url_path_for(
                'arts:lenta')), 302)
    if permissions.FOLLOW_USERS not in current_user['permissions']:
        raise HTTPException(status_code=403,detail='Для вас доступ ограничен.')
    conn = await get_conn(request.app.config)
    if not (page := await parse_page(request)) or \
       not (last := await check_last_banded(
           conn, current_user['id'], page,
           request.app.config.get('ARTS_PER_PAGE', cast=int, default=3))):
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    pagination = await select_banded(
        request, conn, current_user['id'], page,
        request.app.config.get('ARTS_PER_PAGE', cast=int, default=3), last)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'arts/show-banded.html',
        {'request': request,
         'current_user': current_user,
         'pagination': pagination,
         'status': status,
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
    target = dict()
    await check_art(request, conn, current_user, slug, target)
    if not target:
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    rel = None
    if current_user['id'] != target['author_id']:
        rel = await check_rel(conn, current_user['id'], target['author_id'])
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'arts/show-art.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'current_user': current_user,
         'status': status,
         'rel': rel,
         'target': target or None})
