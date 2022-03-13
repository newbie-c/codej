from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, RedirectResponse
from starlette_wtf import csrf_protect, csrf_token

from ..auth.attri import initials, permissions
from ..auth.common import get_current_user
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed, set_flashed
from ..common.pg import get_conn
from ..common.urls import get_next
from .pg import check_last_users, select_users


@csrf_protect
async def admin_users(request):
    conn = await get_conn(request.app.config)
    current_user = await get_current_user(request, conn)
    if current_user is None:
        await conn.close()
        await set_flashed(request, 'Требуется авторизация.')
        return RedirectResponse(
            await get_next(request, request.app.url_path_for('admin:users')),
            302)
    if permissions.FOLLOW_USERS not in current_user['permissions']:
        await conn.close()
        raise HTTPException(
            status_code=403, detail='Для вас доступ ограничен.')
    if not (page:= await parse_page(request)) or \
       not (last := await check_last_users(
            conn, current_user['id'], page,
            request.app.config.get('USERS_PER_PAGE', cast=int, default=3),
            permissions.ADMINISTER_SERVICE in current_user['permissions'])):
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    pagination = await select_users(
        conn, current_user['id'],
        page, request.app.config.get('USERS_PER_PAGE', cast=int, default=3),
        last, permissions.ADMINISTER_SERVICE in current_user['permissions'])
    print(pagination)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'admin/society.html',
        {'request': request,
         'current_user': current_user,
         'pagination': pagination,
         'flashed': await get_flashed(request)})


@csrf_protect
async def set_init_perms(request):
    res = {'empty': True}
    d = await request.form()
    conn = await get_conn(request.app.config)
    current_user = await get_current_user(request, conn)
    if current_user and \
            permissions.ADMINISTER_SERVICE in current_user['permissions']:
        for each in d:
            if each != 'csrf_token':
                await conn.execute(
                    'UPDATE permissions SET init = $1 WHERE name = $2',
                    bool(int(d.get(each))), each)
        res = {'empty': False}
        await set_flashed(request, 'Done!')
    await conn.close()
    return JSONResponse(res)


async def set_service(request):
    conn = await get_conn(request.app.config)
    current_user = await get_current_user(request, conn)
    if current_user is None:
        await conn.close()
        await set_flashed(request, 'Требуется авторизация.')
        url = await get_next(
            request, request.app.url_path_for('admin:settings'))
        return RedirectResponse(url, 302)
    if permissions.ADMINISTER_SERVICE not in current_user['permissions']:
        raise HTTPException(
            status_code=403, detail="Для вас доступ ограничен.")
    perms = await conn.fetch(
        'SELECT * FROM permissions WHERE permission = any($1::varchar[])',
        [permission for permission in initials])
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'admin/settings.html',
        {'request': request,
         'current_user': current_user,
         'perms': perms,
         'token': csrf_token(request),
         'flashed': await get_flashed(request)})
