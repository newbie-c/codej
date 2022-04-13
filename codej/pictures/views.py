import asyncio

from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, RedirectResponse

from ..auth.attri import permissions
from ..auth.common import checkcu
from ..common.aparsers import parse_page
from ..common.flashed import get_flashed, set_flashed
from ..common.pg import get_conn
from ..common.urls import get_next
from .attri import status
from .forms import UploadFile
from .pg import (
    check_last_albums, check_last_pictures, create_new_album, get_album,
    get_user_stat, select_albums, select_pictures)
from .redi import assign_pic_cache
from .tasks import verify_data


async def check_pic(request):
    res = {'empty': True}
    current_user = await checkcu(request)
    if current_user and \
            permissions.UPLOAD_PICTURES in current_user['permissions']:
        d = await request.form()
        cache = await request.app.rc.hgetall(d.get('cache'))
        if cache['res'] and int(cache['uid']) == current_user['id']:
            message = None
            if cache['res'] == 'ready':
                message = 'Изображение успешно загружено.'
            elif cache['res'] == 'size':
                message = 'Запрос отклонён, размер файла больше 5МиБ.'
            elif cache['res'] == 'type':
                message = 'Запрос отклонён, формат не поддерживается.'
            elif cache['res'] == 'repeat':
                url = request.url_for(
                    'pictures:show-album', suffix=cache['suf'])
                message = f'Файл загружен ранее в <a href="{url}">альбом</a>.'
            await set_flashed(request, message)
            await request.app.rc.delete(d.get('cache'))
            res = {'empty': False}
    return JSONResponse(res)


async def show_album(request):
    s = request.path_params.get('suffix')
    current_user = await checkcu(request)
    if current_user is None:
        await set_flashed(request, 'Требуется авторизация.')
        return RedirectResponse(
            await get_next(
                request,
                request.app.url_path_for('pictures:show-album', suffix=s)),
            302)
    if permissions.UPLOAD_PICTURES not in current_user['permissions']:
        raise HTTPException(status_code=403, detail='Доступ ограничен.')
    conn = await get_conn(request.app.config)
    target = await get_album(conn, current_user['id'], s)
    if target is None or \
       not (page := await parse_page(request)) or \
       not (last := await check_last_pictures(
           conn, target['id'], page,
           request.app.config.get('PICTURES_PER_PAGE', cast=int, default=3))):
        await conn.close()
        raise HTTPException(
            status_code=404, detail='Такой страницы у нас нет.')
    pagination = await select_pictures(
        conn, target['id'], page,
        request.app.config.get('PICTURES_PER_PAGE', cast=int, default=3),
        last)
    form = await UploadFile.from_formdata(request)
    if request.method == 'POST':
        cache = await assign_pic_cache(
            request.app.rc, {'res': 0, 'suf': 0, 'uid': current_user['id']})
        asyncio.ensure_future(
            verify_data(request, current_user['id'], target, cache, form))
        await set_flashed(request, 'Верифицирую изображение...')
        await conn.close()
        return request.app.jinja.TemplateResponse(
            'pictures/show-album.html',
            {'request': request,
             'current_user': current_user,
             'target': target,
             'form': None,
             'cache': cache,
             'pagination': pagination,
             'flashed': await get_flashed(request)})
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'pictures/show-album.html',
        {'request': request,
         'current_user': current_user,
         'target': target,
         'pagination': pagination,
         'form': form,
         'flashed': await get_flashed(request)})


async def create_album(request):
    res = {'empty': True}
    d = await request.form()
    if d.get('title') and d.get('state'):
        current_user = await checkcu(request)
        if permissions.UPLOAD_PICTURES in current_user['permissions']:
            conn = await get_conn(request.app.config)
            rep = await conn.fetchval(
                '''SELECT suffix FROM albums
                     WHERE title = $1 AND author_id = $2''',
                d.get('title').strip(), current_user['id'])
            if rep:
                res = {'empty': False,
                       'redirect': request.url_for(
                           'pictures:show-album', suffix=rep)}
                message = 'Альбом уже существует.'
            else:
                new = await create_new_album(
                    conn, current_user['id'],
                    d.get('title').strip(), d.get('state').strip())
                res = {'empty': False,
                       'redirect': request.url_for(
                           'pictures:show-album', suffix=new)}
                message = 'Новый альбом успешно создан.'
            await conn.close()
            await set_flashed(request, message)
    return JSONResponse(res)


async def show_albums(request):
    current_user = await checkcu(request)
    if current_user is None:
        await set_flashed(request, 'Требуется авторизация.')
        return RedirectResponse(
            await get_next(
                request, request.app.url_path_for('pictures:show-albums')),
            302)
    if permissions.UPLOAD_PICTURES not in current_user['permissions']:
        raise HTTPException(status_code=403, detail='Доступ ограничен.')
    conn = await get_conn(request.app.config)
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
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'pictures/show-albums.html',
        {'request': request,
         'flashed': await get_flashed(request),
         'pagination': pagination,
         'status': status,
         'stat': stat,
         'current_user': current_user})
