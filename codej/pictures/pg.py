from datetime import datetime

from ..common.aparsers import (
    iter_pages, parse_last_page, parse_title, parse_units)
from ..common.random import get_unique_s


async def get_user_stat(conn, uid):
    albums = await conn.fetch(
        'SELECT id, volume FROM albums WHERE author_id = $1', uid)
    volume = sum(album.get('volume') for album in albums)
    files = 0
    for album in albums:
        files += await conn.fetchval(
            'SELECT count(*) FROM pictures WHERE album_id = $1',
            album.get('id'))
    return {'albums': len(albums),
            'files': files,
            'volume': await parse_units(volume)}


async def select_albums(conn, current, page, per_page, last):
    query = await conn.fetch(
        '''SELECT title, suffix FROM albums
             WHERE author_id = $1
             ORDER BY changed DESC LIMIT $2 OFFSET $3''',
        current, per_page, per_page*(page-1))
    if query:
        return {'page': page,
                'next': page + 1 if page + 1 <= last else None,
                'prev': page - 1 or None,
                'pages': await iter_pages(page, last),
                'albums': [{'title': record.get('title'),
                            'parsed': await parse_title(
                                record.get('title'), 40),
                            'suffix': record.get('suffix')}
                           for record in query]}
    return None


async def check_last_albums(conn, current, page, per_page):
    return await parse_last_page(
        page, per_page,
        await conn.fetchval(
            'SELECT count(*) FROM albums WHERE author_id = $1', current))


async def create_new_album(conn, uid, title, state):
    now = datetime.utcnow()
    suffix = await get_unique_s(conn, 'albums', 8)
    empty = await conn.fetchval(
        'SELECT id FROM albums WHERE author_id IS NULL')
    if empty:
        await conn.execute(
            '''UPDATE albums SET title = $1,
                                 created = $2,
                                 changed = $2,
                                 suffix = $3,
                                 state = $4,
                                 volume = 0,
                                 author_id = $5 WHERE id = $6''',
            title, now, suffix, state, uid, empty)
    else:
        await conn.execute(
            '''INSERT INTO
                 albums (title, created, changed, suffix, state, author_id)
                 VALUES ($1, $2, $2, $3, $4, $5)''',
            title, now, suffix, state, uid)
    return suffix

