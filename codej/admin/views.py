import os

from datetime import datetime

from starlette.exceptions import HTTPException
from starlette.responses import (
    JSONResponse, FileResponse, PlainTextResponse, RedirectResponse)
from starlette_wtf import csrf_protect, csrf_token

from ..auth.attri import initials, permissions
from ..auth.common import checkcu
from ..common.aparsers import (
    parse_page, parse_pic_filename, parse_redirect, parse_title, parse_units)
from ..common.flashed import get_flashed, set_flashed
from ..common.pg import get_conn
from ..common.urls import get_next
from .forms import CreateUser
from .pg import (
    check_last_pictures, check_last_users, create_user, select_found,
    select_pictures, select_users)


async def find_pic(request):
    res = {'empty': True}
    d = await request.form()
    current_user = await checkcu(request)
    if current_user and \
            permissions.ADMINISTER_SERVICE in current_user['permissions']:
        conn = await get_conn(request.app.config)
        found = {'pictures': [
            {'author': record.get('username'),
             'uploaded': f'{record.get("uploaded").isoformat()}Z',
             'album': record.get('title'),
             'album_parsed64': await parse_title(record.get('title'), 64),
             'filename': record.get('filename'),
             'filename_parsed45': await parse_pic_filename(
                 record.get('filename'), 45),
             'album_state': record.get('state'),
             'width': record.get('width'),
             'height': record.get('height'),
             'format': record.get('format'),
             'volume': await parse_units(record.get('volume')),
             'suffix': record.get('suffix')} for record in await conn.fetch(
             '''SELECT users.username, albums.title,
                       albums.state, pictures.uploaded,
                       pictures.filename, pictures.width,
                       pictures.height, pictures.format,
                       pictures.volume, pictures.suffix
                  FROM users, albums, pictures
                    WHERE users.id = albums.author_id
                      AND albums.id = pictures.album_id
                      AND pictures.suffix LIKE $1''', f"{d.get('value')}%")]}
        res = {'empty': False,
               'html': request.app.jinja.get_template(
                   'admin/found-pics.html').render(
                   found=found, request=request)}
        await conn.close()
    return JSONResponse(res)


async def rem_pic(request):
    res = {'empty': True}
    d = await request.form()
    suffix, page, last = (
        d.get('suffix', 'abc.png'),
        int(d.get('page', '1')), int(d.get('last', '0')))
    current_user = await checkcu(request)
    if current_user and \
            permissions.ADMINISTER_SERVICE in current_user['permissions']:
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            '''SELECT albums.volume AS avol,
                      albums.suffix AS asuffix,
                      pictures.volume AS pvol,
                      pictures.album_id AS aid FROM albums, pictures
                 WHERE albums.id = pictures.album_id
                   AND pictures.suffix = $1''', suffix)
        if target:
            await conn.execute(
                'UPDATE albums SET changed = $1, volume = $2 WHERE id = $3',
                datetime.utcnow(),
                target.get('avol') - target.get('pvol'),
                target.get('aid'))
            await conn.execute(
                'DELETE FROM pictures WHERE suffix = $1', suffix)
            res = {'empty': False,
                   'url': await parse_redirect(
                       request, page, last, 'admin:pictures')}
            await set_flashed(request, 'Файл успешно удалён.')
        await conn.close()
    return JSONResponse(res)


async def admin_pictures(request):
    current_user = await checkcu(request)
    if current_user is None:
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    if permissions.ADMINISTER_SERVICE not in current_user['permissions']:
        raise HTTPException(
            status_code=403, detail='Для вас доступ ограничен.')
    conn = await get_conn(request.app.config)
    if not (page := await parse_page(request)) or \
       not (last := await check_last_pictures(
               conn, current_user['id'], page,
               request.app.config.get(
                   'PICTURES_PER_PAGE', cast=int, default=3))):
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    pagination = await select_pictures(
        conn, current_user['id'],
        page, request.app.config.get(
            'PICTURES_PER_PAGE', cast=int, default=3), last)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'admin/pictures.html',
        {'request': request,
         'current_user': current_user,
         'pagination': pagination,
         'flashed': await get_flashed(request)})


async def show_log(request):
    current_user = await checkcu(request)
    fn = request.path_params['filename']
    if current_user is None or fn not in ('access.log', 'previous.log'):
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    if permissions.ADMINISTER_SERVICE not in current_user['permissions']:
        raise HTTPException(
            status_code=403, detail='Для вас доступ ограничен.')
    if fn == 'access.log':
        fn = f'/var/log/nginx/{fn}'
    else:
        fn = '/var/log/nginx/access.log.1'
    if os.path.exists(fn):
        response = FileResponse(fn)
    else:
        response = PlainTextResponse('Файл не существует.')
    return response


async def find_user(request):
    res = {'empty': True}
    d = await request.form()
    current_user = await checkcu(request)
    if current_user and \
            permissions.FOLLOW_USERS in current_user['permissions']:
        conn = await get_conn(request.app.config)
        found = await select_found(
            conn, current_user['id'], d.get('value'),
            permissions.ADMINISTER_SERVICE in current_user['permissions'])
        res = {'empty': False,
               'html': request.app.jinja.get_template(
                   'admin/found-users.html').render(
                       found=found, request=request)}
        await conn.close()
    return JSONResponse(res)


@csrf_protect
async def admin_users(request):
    current_user = await checkcu(request)
    if current_user is None:
        await set_flashed(request, 'Требуется авторизация.')
        return RedirectResponse(
            await get_next(request, request.app.url_path_for('admin:users')),
            302)
    if permissions.FOLLOW_USERS not in current_user['permissions']:
        raise HTTPException(
            status_code=403, detail='Для вас доступ ограничен.')
    conn = await get_conn(request.app.config)
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
    form = None
    if permissions.ADMINISTER_SERVICE in current_user['permissions']:
        form = await CreateUser.from_formdata(request)
        if await form.validate_on_submit():
            if await conn.fetchval(
                    'SELECT username FROM users WHERE username = $1',
                    form.username.data):
                await conn.close()
                await set_flashed(
                    request,
                    f'Псевдоним "{form.username.data}" уже занят, \
                      нужно придумать другой.')
                return RedirectResponse(request.url_for('admin:users'), 302)
            acc = await conn.fetchval(
                'SELECT user_id FROM accounts WHERE address = $1',
                form.address.data)
            swapped = await conn.fetchval(
                'SELECT swap FROM accounts WHERE swap = $1',
                form.address.data)
            if acc or swapped:
                await conn.close()
                await set_flashed(
                    request,
                    f'Адрес "{form.address.data}" уже используется, \
                      запрос отклонён.')
                return RedirectResponse(request.url_for('admin:users'), 302)
            await create_user(
                conn, form.username.data,
                form.password.data, form.address.data)
            await conn.close()
            await set_flashed(request, 'Аккаунт зарегистрирован.')
            return RedirectResponse(
                request.url_for('profile', username=form.username.data), 302)
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'admin/society.html',
        {'request': request,
         'current_user': current_user,
         'pagination': pagination,
         'form': form,
         'flashed': await get_flashed(request)})


@csrf_protect
async def set_init_perms(request):
    res = {'empty': True}
    d = await request.form()
    current_user = await checkcu(request)
    if current_user and \
            permissions.ADMINISTER_SERVICE in current_user['permissions']:
        conn = await get_conn(request.app.config)
        for each in d:
            if each != 'csrf_token':
                await conn.execute(
                    'UPDATE permissions SET init = $1 WHERE name = $2',
                    bool(int(d.get(each))), each)
        res = {'empty': False}
        await conn.close()
        await set_flashed(request, 'Done!')
    return JSONResponse(res)


async def set_service(request):
    current_user = await checkcu(request)
    if current_user is None:
        await set_flashed(request, 'Требуется авторизация.')
        url = await get_next(
            request, request.app.url_path_for('admin:settings'))
        return RedirectResponse(url, 302)
    if permissions.ADMINISTER_SERVICE not in current_user['permissions']:
        raise HTTPException(
            status_code=403, detail="Для вас доступ ограничен.")
    conn = await get_conn(request.app.config)
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
