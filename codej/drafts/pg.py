import asyncio
import functools

from datetime import datetime

from ..common.random import get_unique_s
from .attri import status
from .slugs import check_max, parse_match, make


async def create_d(conn, title, uid):
    suffix = await get_unique_s(conn, 'articles', 8)
    slug = await check_slug(conn, title)
    now = datetime.utcnow()
    empty = await conn.fetchval(
        'SELECT id FROM articles WHERE author_id IS NULL')
    if empty:
        await conn.execute(
            '''UPDATE articles
                 SET title = $1, slug = $2, suffix = $3,
                     edited = $4, state = $5, author_id = $6
                 WHERE id = $7''',
            title, slug, suffix, now, status.draft, uid, empty)
    else:
        await conn.execute(
            '''INSERT INTO articles
               (title, slug, suffix, edited, state, author_id)
               VALUES ($1, $2, $3, $4, $5, $6)''',
            title, slug, suffix, now, status.draft, uid)
    return slug


async def check_slug(conn, title):
    loop = asyncio.get_running_loop()
    slug = await loop.run_in_executor(
        None, functools.partial(make, title))
    match = await conn.fetch(
        'SELECT slug FROM articles WHERE slug LIKE $1', f'{slug}%')
    match = await loop.run_in_executor(
        None, functools.partial(parse_match, match))
    if not match or slug not in match:
        return slug
    maxi = await loop.run_in_executor(
        None, functools.partial(check_max, match, slug))
    return f'{slug}-{maxi+1}'
