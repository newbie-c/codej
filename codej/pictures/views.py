import asyncio

from datetime import datetime

from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, RedirectResponse

from ..auth.attri import permissions
from ..auth.common import checkcu
from ..common.aparsers import parse_page, parse_redirect
from ..common.flashed import get_flashed, set_flashed
from ..common.pg import get_conn
from ..common.urls import get_next
from .attri import status
from .forms import UploadFile
from .pg import (
    check_last_albums, check_last_pictures, create_new_album, get_album,
    get_pic_stat, get_user_stat, select_albums, select_pictures)
from .redi import assign_pic_cache
from .tasks import verify_data


async def remove_pic(request):
    res = {'empty': True}
    d = await request.form()
    suffix, page, last = (
        d.get('suffix', 'abc.png'),
        int(d.get('page', '1')), int(d.get('last', '0')))
    current_user = await checkcu(request)
    if current_user and \
            permissions.UPLOAD_PICTURES in current_user['permissions']:
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            '''SELECT albums.volume AS avol,
                      albums.suffix AS asuffix,
                      pictures.volume AS pvol,
                      pictures.album_id AS aid FROM albums, pictures
                 WHERE albums.id = pictures.album_id
                   AND albums.author_id = $1
                   AND pictures.suffix = $2''',
            current_user['id'], suffix)
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
                       request, page, last,
                       'pictures:show-album', suffix=target['asuffix'])}
            await set_flashed(request, '???????? ?????????????? ????????????.')
        await conn.close()
    return JSONResponse(res)


async def find_album(request):
    res = {'empty': True}
    current_user = await checkcu(request)
    suffix = (await request.form()).get('suffix')
    if suffix and current_user and \
            permissions.UPLOAD_PICTURES in current_user['permissions']:
        conn = await get_conn(request.app.config)
        s = await conn.fetchval(
            '''SELECT albums.suffix FROM albums, pictures
                 WHERE albums.id = pictures.album_id
                 AND pictures.suffix = $1 AND albums.author_id = $2''',
            suffix, current_user['id'])
        await conn.close()
        if s:
            res = {'empty': False,
                   'url': request.url_for('pictures:show-album', suffix=s)}
    return JSONResponse(res)


async def show_pic_stat(request):
    res = {'empty': True}
    d = await request.form()
    current_user = await checkcu(request)
    conn = await get_conn(request.app.config)
    picture = await get_pic_stat(conn, current_user['id'], d.get('suffix'))
    if current_user and picture and \
            permissions.UPLOAD_PICTURES in current_user['permissions']:
        res = {'empty': False,
               'html': request.app.jinja.get_template(
                   'pictures/pic-stat.html').render(
                       request=request, picture=picture)}
    await conn.close()
    return JSONResponse(res)


async def show_user_stat(request):
    res = {'empty': True}
    current_user = await checkcu(request)
    d = await request.form()
    uid = int(d.get('uid', '0'))
    if current_user and \
            uid == current_user['id'] and \
            permissions.UPLOAD_PICTURES in current_user['permissions']:
        conn = await get_conn(request.app.config)
        stat = await get_user_stat(conn, current_user['id'])
        res = {'empty': False,
               'html': request.app.jinja.get_template(
                   'pictures/user-statistic.html').render(
                   user=current_user, stat=stat)}
        await conn.close()
    return JSONResponse(res)


async def show_album_stat(request):
    res = {'empty': True}
    current_user = await checkcu(request)
    if current_user and \
            permissions.UPLOAD_PICTURES in current_user['permissions']:
        d = await request.form()
        conn = await get_conn(request.app.config)
        target = await get_album(
            conn, current_user['id'], suffix=d.get('suffix'))
        if target:
            res = {'empty': False,
                   'html': request.app.jinja.get_template(
                       'pictures/album-statistic.html').render(
                           request=request, target=target, status=status)}
        await conn.close()
    return JSONResponse(res)


async def rename_album(request):
    res = {'empty': True}
    current_user = await checkcu(request)
    if current_user and \
            permissions.UPLOAD_PICTURES in current_user['permissions']:
        d = await request.form()
        conn = await get_conn(request.app.config)
        target = await get_album(
            conn, current_user['id'], aid=int(d.get('album')))
        if target and len(d.get('title')) <= 100  and \
                d.get('title') != target['title']:
            await conn.execute(
                'UPDATE albums SET title = $1 WHERE id = $2',
                d.get('title'), target['id'])
            res = {'empty': False}
        await conn.close()
    return JSONResponse(res)


async def change_state(request):
    res = {'empty': True}
    current_user = await checkcu(request)
    if current_user and \
            permissions.UPLOAD_PICTURES in current_user['permissions']:
        d = await request.form()
        conn = await get_conn(request.app.config)
        target = await get_album(
            conn, current_user['id'], aid=int(d.get('album')))
        if target:
            await conn.execute(
                'UPDATE albums SET state = $1 WHERE id = $2',
                d.get('state'), target['id'])
            target = await get_album(
                conn, current_user['id'], aid=target['id'])
            res = {'empty': False,
                   'html': request.app.jinja.get_template(
                       'pictures/album-statistic.html').render(
                           request=request, target=target, status=status)}
        await conn.close()
    return JSONResponse(res)


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
                message = '?????????????????????? ?????????????? ??????????????????.'
            elif cache['res'] == 'size':
                message = '???????????? ????????????????, ???????????? ?????????? ???????????? 5??????.'
            elif cache['res'] == 'type':
                message = '???????????? ????????????????, ???????????? ???? ????????????????????????????.'
            elif cache['res'] == 'repeat':
                url = request.url_for(
                    'pictures:show-album', suffix=cache['suf'])
                message = f'???????? ???????????????? ?????????? ?? <a href="{url}">????????????</a>.'
            await set_flashed(request, message)
            await request.app.rc.delete(d.get('cache'))
            res = {'empty': False}
    return JSONResponse(res)


async def show_album(request):
    s = request.path_params.get('suffix')
    current_user = await checkcu(request)
    if current_user is None:
        await set_flashed(request, '?????????????????? ??????????????????????.')
        return RedirectResponse(
            await get_next(
                request,
                request.app.url_path_for('pictures:show-album', suffix=s)),
            302)
    if permissions.UPLOAD_PICTURES not in current_user['permissions']:
        raise HTTPException(status_code=403, detail='???????????? ??????????????????.')
    conn = await get_conn(request.app.config)
    target = await get_album(conn, current_user['id'], suffix=s)
    if target is None or \
       not (page := await parse_page(request)) or \
       not (last := await check_last_pictures(
           conn, target['id'], page,
           request.app.config.get('PICTURES_PER_PAGE', cast=int, default=3))):
        await conn.close()
        raise HTTPException(
            status_code=404, detail='?????????? ???????????????? ?? ?????? ??????.')
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
        await set_flashed(request, '?????????????????????? ??????????????????????...')
        await conn.close()
        return request.app.jinja.TemplateResponse(
            'pictures/show-album.html',
            {'request': request,
             'current_user': current_user,
             'target': target,
             'form': None,
             'cache': cache,
             'pagination': pagination,
             'status': status,
             'flashed': await get_flashed(request)})
    await conn.close()
    return request.app.jinja.TemplateResponse(
        'pictures/show-album.html',
        {'request': request,
         'current_user': current_user,
         'target': target,
         'pagination': pagination,
         'form': form,
         'status': status,
         'flashed': await get_flashed(request)})


async def create_album(request):
    res = {'empty': True}
    d = await request.form()
    if d.get('title') and d.get('state'):
        current_user = await checkcu(request)
        if current_user and \
                permissions.UPLOAD_PICTURES in current_user['permissions']:
            conn = await get_conn(request.app.config)
            rep = await conn.fetchval(
                '''SELECT suffix FROM albums
                     WHERE title = $1 AND author_id = $2''',
                d.get('title').strip(), current_user['id'])
            if rep:
                res = {'empty': False,
                       'redirect': request.url_for(
                           'pictures:show-album', suffix=rep)}
                message = '???????????? ?????? ????????????????????.'
            else:
                new = await create_new_album(
                    conn, current_user['id'],
                    d.get('title').strip(), d.get('state').strip())
                res = {'empty': False,
                       'redirect': request.url_for(
                           'pictures:show-album', suffix=new)}
                message = '?????????? ???????????? ?????????????? ????????????.'
            await conn.close()
            await set_flashed(request, message)
    return JSONResponse(res)


async def show_albums(request):
    current_user = await checkcu(request)
    if current_user is None:
        await set_flashed(request, '?????????????????? ??????????????????????.')
        return RedirectResponse(
            await get_next(
                request, request.app.url_path_for('pictures:show-albums')),
            302)
    if permissions.UPLOAD_PICTURES not in current_user['permissions']:
        raise HTTPException(status_code=403, detail='???????????? ??????????????????.')
    conn = await get_conn(request.app.config)
    if not (page := await parse_page(request)) or \
       not (last := await check_last_albums(
           conn, current_user['id'], page,
           request.app.config.get('ALBUMS_PER_PAGE', cast=int, default=3))):
        await conn.close()
        raise HTTPException(
            status_code=404, detail='?????????? ???????????????? ?? ?????? ??????.')
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
