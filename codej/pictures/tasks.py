import asyncio
import functools
import io

from datetime import datetime

from PIL import Image

from ..common.pg import get_conn
from ..common.aparsers import parse_filename
from ..common.random import get_unique_s
from .redi import assign_pic_cache


def read_data(binary):
    try:
        image = Image.open(io.BytesIO(binary))
    except OSError:
        image = None
    if image and image.format not in ('JPEG', 'PNG', 'GIF'):
        image.close()
        image = None
    return image


async def verify_data(request, uid, album, cache, form):
    filename = await parse_filename(form.image.data.filename, 128)
    now = datetime.utcnow()
    binary = await form.image.data.read()
    if len(binary) > 5 * pow(1024, 2):
        await form.image.data.close()
        await assign_pic_cache(
            request.app.rc,
            {'res': 'size', 'suf': 0, 'uid': uid},
            prefix=None, name=cache)
        return 'Done!'
    loop = asyncio.get_running_loop()
    image = await loop.run_in_executor(
        None, functools.partial(read_data, binary))
    if image is None:
        await form.image.data.close()
        await assign_pic_cache(
            request.app.rc,
            {'res': 'type', 'suf': 0, 'uid': uid},
            prifix=None, name=cache)
        return 'Done!'
    conn = await get_conn(request.app.config)
    replica = await conn.fetchrow(
        '''SELECT author_id, suffix, picture
             FROM (SELECT albums.author_id, albums.suffix, pictures.picture
                     FROM albums LEFT JOIN pictures
                     ON albums.id = pictures.album_id) AS between
             WHERE author_id = $1 AND picture = $2''', uid, binary)
    if replica:
        await loop.run_in_executor(
            None, functools.partial(image.close))
        await form.image.data.close()
        await assign_pic_cache(
            request.app.rc,
            {'res': 'repeat', 'suf': replica.get('suffix'), 'uid': uid},
            prefix=None, name=cache)
        await conn.close()
        return 'Done!'
    e = {'JPEG': '.jpg', 'PNG': '.png', 'GIF': '.gif'}
    suffix = await get_unique_s(conn, 'pictures', 10, ext=e.get(image.format))
    await conn.execute(
        '''INSERT INTO
             pictures (uploaded, picture, filename, width,
                       height, format, volume, suffix, album_id)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)''',
        now, binary, filename, image.width, image.height,
        image.format, len(binary), suffix, album['id'])
    await conn.execute(
        'UPDATE albums SET changed = $1, volume = $2 WHERE id = $3',
        now, album['volume_']+len(binary), album['id'])
    await assign_pic_cache(
        request.app.rc,
        {'res': 'ready', 'suf': 0, 'uid': uid},
        prefix=None, name=cache)
    await loop.run_in_executor(
        None, functools.partial(image.close))
    await form.image.data.close()
    await conn.close()
    return 'Done!'
