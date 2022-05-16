import asyncio
import functools

from datetime import datetime

from ..common.aparsers import (
    iter_pages, parse_last_page, parse_title)
from ..common.avatar import get_ava_url
from ..common.random import get_unique_s
from .attri import status
from .md import check_text, parse_md
from .slugs import check_max, parse_match, make


async def save_par(conn, art, text, code):
    loop = asyncio.get_running_loop()
    text, spec = await loop.run_in_executor(
        None, functools.partial(check_text, text, code))
    if spec and text:
        if await conn.fetchrow(
                '''SELECT num FROM paragraphs
                     WHERE mdtext = $1 AND article_id = $2''', text, art):
            text = None
    if text:
        last = await conn.fetchval(
            '''SELECT num FROM paragraphs
                 WHERE article_id = $1 ORDER BY num DESC''', art)
        if last is None:
            last = -1
        await conn.execute(
            '''INSERT INTO paragraphs (num, mdtext, article_id)
                 VALUES ($1, $2, $3)''', last+1, text, art)
        pars = await conn.fetch(
            '''SELECT mdtext FROM paragraphs
                 WHERE article_id = $1 ORDER BY num ASC''', art)
        html = await loop.run_in_executor(
            None, functools.partial(parse_md, pars))
        if html:
            await conn.execute(
                'UPDATE articles SET html = $1 WHERE id = $2',
                html, art)
        return html


async def select_drafts(request, conn, current, page, per_page, last):
    query = await conn.fetch(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                  a.edited, a.state, a.commented, a.viewed,
                  accounts.ava_hash, users.username
             FROM articles AS a, users, accounts
             WHERE a.author_id = users.id
               AND accounts.user_id = a.author_id
               AND a.author_id = $1
               AND (a.state = $2 OR a.state = $3)
             ORDER BY a.edited DESC LIMIT $4 OFFSET $5''',
        current, status.draft, status.mod, per_page, per_page*(page-1))
    if query:
        return {'page': page,
                'next': page + 1 if page + 1 <= last else None,
                'prev': page - 1 or None,
                'pages': await iter_pages(page, last),
                'articles': [
                    {'id': record.get('id'),
                     'title': record.get('title'),
                     'title80': await parse_title(record.get('title'), 80),
                     'slug': record.get('slug'),
                     'suffix': record.get('suffix'),
                     'summary': record.get('summary'),
                     'published': f'{record.get("published").isoformat()}Z'
                     if record.get('published') else None,
                     'edited': f'{record.get("edited").isoformat()}Z',
                     'state': record.get('state'),
                     'commented': record.get('commented'),
                     'viewed': record.get('viewed'),
                     'author': record.get('username'),
                     'ava': await get_ava_url(
                         request, record.get('ava_hash'), size=88),
                     'likes': 0,
                     'dislikes': 0,
                     'commentaries': 0} for record in query]}


async def check_last_drafts(conn, current, page, per_page):
    return await parse_last_page(
        page, per_page, await conn.fetchval(
            '''SELECT count(*) FROM articles
                 WHERE author_id = $1
                   AND (state = $2 OR state = $3)''',
            current, status.draft, status.mod))


async def check_article(request, conn, slug):
    query = await conn.fetchrow(
        '''SELECT articles.id,
                  articles.title,
                  articles.slug,
                  articles.suffix,
                  articles.html,
                  articles.summary,
                  articles.meta,
                  articles.published,
                  articles.edited,
                  articles.state,
                  articles.commented,
                  articles.viewed,
                  articles.author_id,
                  accounts.ava_hash,
                  users.username FROM articles, accounts, users
             WHERE articles.slug = $1
               AND users.id = articles.author_id
               AND accounts.user_id = articles.author_id''', slug)
    if query:
        return {'id': query.get('id'),
                'title': query.get('title'),
                'title80': await parse_title(query.get('title'), 80),
                'slug': query.get('slug'),
                'suffix': query.get('suffix'),
                'html': query.get('html'),
                'summary': query.get('summary'),
                'meta': query.get('meta'),
                'published': f'{query.get("published").isoformat()}Z'
                if query.get('published') else None,
                'edited': f'{query.get("edited").isoformat()}Z',
                'state': query.get('state'),
                'commented': query.get('commented'),
                'viewed': query.get('viewed'),
                'author': query.get('username'),
                'author_id': query.get('author_id'),
                'ava': await get_ava_url(
                    request, query.get('ava_hash'), size=88),
                'likes': 0,
                'dislikes': 0,
                'commentaries': 0}


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
