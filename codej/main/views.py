import os

from starlette.exceptions import HTTPException
from starlette.responses import (
    FileResponse, JSONResponse, PlainTextResponse, Response, RedirectResponse)
from starlette_wtf import csrf_protect, csrf_token

from ..auth.attri import (
    average, fix_extra_permissions, groups, permissions, roots)
from ..auth.common import checkcu
from ..common.flashed import get_flashed, set_flashed
from ..common.parsers import parse_address
from ..common.pg import get_conn
from ..common.urls import get_next
from .pg import check_friends, filter_target_user
from .redi import change_udata
from .tools import check_state

robots = """User-agent: *
Disallow: /
"""


async def show_picture(request):
    current_user = await checkcu(request)
    conn = await get_conn(request.app.config)
    target = await conn.fetchrow(
        '''SELECT albums.state, albums.author_id, pictures.suffix,
                  pictures.picture, pictures.format FROM albums, pictures
             WHERE pictures.suffix = $1
               AND albums.id = pictures.album_id''',
        request.path_params.get('suffix'))
    base = os.path.dirname(os.path.dirname(__file__))
    if target is None:
        response = FileResponse(
            os.path.join(base, 'static', 'images', '404.jpg'))
        response.headers.append(
            'cache-control',
            'max-age=0, no-store, no-cache, must-revalidate')
    else:
        if await check_state(conn, target, current_user):
            response = Response(
                target.get('picture'),
                media_type=f'image/{target.get("format").lower()}')
            response.headers.append(
                'cache-control',
                'public, max-age={0}'.format(
                    request.app.config.get(
                        'SEND_FILE_MAX_AGE', cast=int, default=0)))
        else:
            response = FileResponse(
                os.path.join(base, 'static', 'images', '403.jpg'))
            response.headers.append(
                'cache-control',
                'max-age=0, no-store, no-cache, must-revalidate')
    await conn.close()
    return response


async def make_friend(request):
    res = {'empty': True}
    d = await request.form()
    current_user = await checkcu(request)
    if current_user and \
            permissions.FOLLOW_USERS in current_user['permissions']:
        conn = await get_conn(request.app.config)
        friend = int(d.get('friend'))
        fname = await conn.fetchval(
            'SELECT username FROM users WHERE id = $1', friend)
        if await check_friends(conn, current_user['id'], friend):
            await conn.execute(
                'DELETE FROM friends WHERE author_id = $1 AND friend_id = $2',
                current_user['id'], friend)
            message = f'{fname} удалён из списка ваших друзей.'
        else:
            await conn.execute(
                '''INSERT INTO friends (author_id, friend_id)
                     VALUES ($1, $2)''', current_user['id'], friend)
            message = f'{fname} добавлен в список ваших друзей.'
        await conn.close()
        await set_flashed(request, message)
        res = {'empty': False}
    return JSONResponse(res)


@csrf_protect
async def show_profile(request):
    current_user = await checkcu(request)
    if current_user is None:
        await set_flashed(request, 'Требуется авторизация.')
        return RedirectResponse(
            await get_next(request, request.app.url_path_for(
                'profile', username=request.path_params['username'])), 302)
    conn = await get_conn(request.app.config)
    target = await filter_target_user(request, conn)
    is_friend = await check_friends(conn, current_user['id'], target['uid'])
    if target is None:
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    if current_user['id'] != target['uid'] and \
            permissions.FOLLOW_USERS not in current_user['permissions']:
        await conn.close()
        raise HTTPException(
            status_code=403, detail='Для вас доступ ограничен.')
    if request.method == 'POST' and \
            (current_user['username'] != target['username'] and
             (permissions.ADMINISTER_SERVICE in current_user['permissions'] or
              (permissions.CHANGE_USER_ROLE in current_user['permissions'] and
               permissions.CHANGE_USER_ROLE not in target['permissions']) or
            (current_user['group'] == groups.keeper and
             target['group'] != groups.keeper and
             permissions.ADMINISTER_SERVICE not in target['permissions']))):
        form = await request.form()
        chquery = 'UPDATE users SET permissions = $1 WHERE username = $2'
        data = f'data:{target.get("uid")}'
        if form.get('cannot-log-in', None):
            await conn.execute(
                chquery, [permissions.CANNOT_LOG_IN], target['username'])
            await change_udata(
                request.app.rc, data, [permissions.CANNOT_LOG_IN])
        elif form.get('administer-service', None):
            await conn.execute(
                chquery, roots, target['username'])
            await change_udata(
                request.app.rc, data, roots)
        else:
            extra = await fix_extra_permissions(
                current_user, target['permissions'])
            assigned = list()
            for each in average:
                if form.get(each, None):
                    assigned.append(average[each])
            if (permissions.CHANGE_USER_ROLE in assigned or
                permissions.BLOCK_ENTITY in assigned) \
                    and permissions.FOLLOW_USERS not in assigned:
                assigned.append(permissions.FOLLOW_USERS)
            assigned = assigned + extra
            await conn.execute(
                chquery, assigned or [permissions.CANNOT_LOG_IN],
                target['username'])
            await change_udata(
                request.app.rc, data, assigned or [permissions.CANNOT_LOG])
        await conn.close()
        await set_flashed(
            request, f'Разрешения {target["username"]} успешно изменены.')
        return RedirectResponse(
            request.url_for('profile', username=target['username']), 302)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'main/profile.html',
        {'request': request,
         'current_user': current_user,
         'target': target,
         'is_friend': is_friend,
         'parse_address': parse_address,
         'csrf_token': csrf_token(request),
         'flashed': await get_flashed(request)})


async def show_index(request):
    current_user = await checkcu(request)
    print(current_user)
    return request.app.jinja.TemplateResponse(
        'main/index.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'target': None,
         'current_user': current_user})


async def show_robots(request):
    if request.method == 'GET':
        return PlainTextResponse(robots)


async def show_favicon(request):
    if request.method == 'GET':
        base = os.path.dirname(os.path.dirname(__file__))
        return FileResponse(
            os.path.join(base, 'static', 'images', 'favicon.ico'))
