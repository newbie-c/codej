import os
from starlette.exceptions import HTTPException
from starlette.responses import (
    FileResponse, PlainTextResponse, RedirectResponse)
from starlette_wtf import csrf_protect, csrf_token

from ..auth.attri import (
    average, fix_extra_permissions, groups, permissions, roots)
from ..auth.common import get_current_user
from ..common.flashed import get_flashed, set_flashed
from ..common.parsers import parse_address
from ..common.pg import get_conn
from ..common.urls import get_next
from .pg import filter_target_user

robots = """User-agent: *
Disallow: /
"""


@csrf_protect
async def show_profile(request):
    conn = await get_conn(request.app.config)
    current_user = await get_current_user(request, conn)
    if current_user is None:
        await set_flashed(request, 'Требуется авторизация.')
        await conn.close()
        return RedirectResponse(
            await get_next(request, request.app.url_path_for(
                'profile', username=request.path_params['username'])), 302)
    target = await filter_target_user(request, conn)
    if target is None:
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    if current_user['username'] != target['username'] and \
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
        if form.get('cannot-log-in', None):
            await conn.execute(
                chquery, [permissions.CANNOT_LOG_IN], target['username'])
        elif form.get('administer-service', None):
            await conn.execute(
                chquery, roots, target['username'])
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
         'parse_address': parse_address,
         'csrf_token': csrf_token(request),
         'flashed': await get_flashed(request)})


async def show_index(request):
    conn = await get_conn(request.app.config)
    current_user = await get_current_user(request, conn)
    await conn.close()
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
