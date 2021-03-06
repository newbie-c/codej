import asyncio
import functools

from datetime import datetime

from ..common.aparsers import (
    iter_pages, parse_last_page, parse_title)
from ..common.avatar import get_ava_url
from ..common.random import get_unique_s
from .attri import status
from .md import check_text, parse_md
from .parse import parse_art_query, parse_arts_query
from .slugs import check_max, parse_match, make


async def prepend_par(conn, art, num, text, code):
    loop = asyncio.get_running_loop()
    text, spec = await loop.run_in_executor(
        None, functools.partial(check_text, text, code))
    if spec and text:
        if await conn.fetchrow(
            '''SELECT num FROM paragraphs
                 WHERE mdtext = $1 AND article_id = $2''', text, art):
            text = None
    if text:
        after = await conn.fetch(
            '''SELECT num FROM paragraphs
                 WHERE article_id = $1 AND num >= $2
                 ORDER BY num DESC''', art, num)
        if after:
            last = after[0].get('num')
        else:
            last = num
        i = last
        while i >= num:
            await conn.execute(
                '''UPDATE paragraphs SET num = num + 1
                     WHERE num = $1 AND article_id = $2''', i, art)
            i -= 1
        await conn.execute(
            '''INSERT INTO paragraphs (mdtext, article_id, num)
                 VALUES ($1, $2, $3)''',
            text, art, num)
        pars = await conn.fetch(
            '''SELECT mdtext FROM paragraphs
                 WHERE article_id = $1 ORDER BY num ASC''', art)
        html = await loop.run_in_executor(
            None, functools.partial(parse_md, pars))
        if html:
            await conn.execute(
                'UPDATE articles SET html = $1, edited = $2 WHERE id = $3',
                html, datetime.utcnow(), art)
        return html


async def remove_this(conn, art, num):
    after = await conn.fetch(
        '''SELECT num FROM paragraphs
             WHERE article_id = $1 AND num > $2
             ORDER BY num DESC''', art, num)
    if after:
        last = after[0].get('num')
    else:
        last = num
    if last:
        await conn.execute(
            'DELETE FROM paragraphs WHERE num = $1 AND article_id = $2',
            num, art)
        if last > num:
            i = num + 1
            while i <= last:
                await conn.execute(
                    '''UPDATE paragraphs SET num = num - 1
                         WHERE num = $1 AND article_id = $2''', i, art)
                i += 1
        pars = await conn.fetch(
            '''SELECT mdtext FROM paragraphs
                 WHERE article_id = $1 ORDER BY num ASC''', art)
        loop = asyncio.get_running_loop()
        html = await loop.run_in_executor(
            None, functools.partial(parse_md, pars))
        await conn.execute(
            'UPDATE articles SET html = $1, edited = $2 WHERE id = $3',
            html, datetime.utcnow(), art)
    return last


async def change_par(conn, target, text, code):
    if target.get('mdtext') == text:
        return None
    loop = asyncio.get_running_loop()
    text, spec = await loop.run_in_executor(
        None, functools.partial(check_text, text, code))
    if spec and text:
        if await conn.fetchrow(
                '''SELECT num FROM paragraphs
                     WHERE mdtext = $1 AND article_id = $2''',
                text, target.get('article_id')):
            text = None
    if text:
        await conn.execute(
            '''UPDATE paragraphs SET mdtext = $1
                 WHERE article_id = $2 AND num = $3''',
            text, target.get('article_id'), target.get('num'))
        pars = await conn.fetch(
            '''SELECT mdtext FROM paragraphs
                 WHERE article_id = $1 ORDER BY num ASC''',
            target.get('article_id'))
        html = await loop.run_in_executor(
            None, functools.partial(parse_md, pars))
        if html:
            await conn.execute(
                'UPDATE articles SET html = $1, edited = $2 WHERE id = $3',
                html, datetime.utcnow(), target.get('article_id'))
        return html


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
                'UPDATE articles SET html = $1, edited = $2 WHERE id = $3',
                html, datetime.utcnow(), art)
        return html


async def select_labeled_drafts(
        request, conn, current, label, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                  a.edited, a.state, a.commented, a.viewed,
                  accounts.ava_hash, users.username
             FROM articles AS a, users, accounts, labels, als
             WHERE a.author_id = users.id
               AND accounts.user_id = a.author_id
               AND a.author_id = $1
               AND a.id = als.article_id
               AND labels.label = $2
               AND labels.id = als.label_id
               AND a.state IN ($3, $4)
            ORDER BY a.edited DESC LIMIT $5 OFFSET $6''',
        current, label, status.draft, status.mod, per_page, per_page*(page-1))
    if query:
        await parse_arts_query(request, conn, query, target, page, last)


async def select_drafts(request, conn, current, target, page, per_page, last):
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
        await parse_arts_query(request, conn, query, target, page, last)


async def check_last_labeled(conn, current, label, page, per_page):
    return await parse_last_page(page, per_page, await conn.fetchval(
        '''SELECT count(*) FROM articles, labels, als
             WHERE articles.author_id = $1
               AND articles.id = als.article_id
               AND labels.label = $2
               AND labels.id = als.label_id
               AND articles.state IN ($3, $4)''',
        current, label, status.draft, status.mod))


async def check_last_drafts(conn, current, page, per_page):
    return await parse_last_page(
        page, per_page, await conn.fetchval(
            '''SELECT count(*) FROM articles
                 WHERE author_id = $1
                   AND (state = $2 OR state = $3)''',
            current, status.draft, status.mod))


async def check_article(request, conn, slug, cuid, target):
    query = await conn.fetchrow(
        '''SELECT articles.id, articles.title, articles.slug,
                  articles.suffix, articles.html, articles.summary,
                  articles.meta, articles.published, articles.edited,
                  articles.state, articles.commented, articles.viewed,
                  articles.author_id, accounts.ava_hash, users.username
             FROM articles, accounts, users
             WHERE articles.slug = $1
               AND articles.author_id = $2
               AND users.id = articles.author_id
               AND accounts.user_id = articles.author_id''',
               slug, cuid)
    if query:
        await parse_art_query(request, conn, query, target)


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
