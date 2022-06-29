from ..auth.attri import permissions
from ..common.aparsers import iter_pages, parse_last_page, parse_title
from ..common.avatar import get_ava_url
from ..drafts.attri import status


async def check_rel(conn, cu, authid):
    f = await conn.fetchrow(
        '''SELECT author_id, follower_id FROM followers
             WHERE author_id = $1 AND follower_id = $2''', authid, cu)
    b = await conn.fetchrow(
        '''SELECT target_id, blocker_id FROM blockers
             WHERE target_id = $1 AND blocker_id = $2''', cu, authid)
    bb = await conn.fetchrow(
        '''SELECT target_id, blocker_id FROM blockers
             WHERE target_id = $1 AND blocker_id = $2''', authid, cu)
    return {'follower': bool(f),
            'blocker': bool(b),
            'blocked': bool(bb)}


async def select_auth(request, conn, auth, current_user, page, per_page, last):
    if permissions.BLOCK_ENTITY in current_user['permissions'] or \
            auth['id'] == current_user['id']:
        q = await conn.fetch(
            '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                      a.edited, a.state, a.commented, a.viewed,
                      accounts.ava_hash, users.username
                 FROM articles AS a, users, accounts
                 WHERE a.author_id = users.id
                   AND a.author_id = $1
                   AND accounts.user_id = a.author_id
                   AND a.state IN ($2, $3, $4)
                ORDER BY a.published DESC LIMIT $5 OFFSET $6''',
            auth['id'], status.pub, status.priv, status.hidden,
            per_page, per_page*(page-1))
    else:
        q = await conn.fetch(
            '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                      a.edited, a.state, a.commented, a.viewed,
                      accounts.ava_hash, users.username
                 FROM articles AS a, users, accounts
                 WHERE a.author_id = users.id
                   AND a.author_id = $1
                   AND accounts.user_id = a.author_id
                   AND a.state IN ($2, $3)
                ORDER BY a.published DESC LIMIT $4 OFFSET $5''',
            auth['id'], status.pub, status.priv, per_page, per_page*(page-1))
    if q:
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
                     'likes': await conn.fetchval(
                        '''SELECT count(*) FROM art_likes
                             WHERE article_id = $1''', record.get('id')),
                     'dislikes': await conn.fetchval(
                        '''SELECT count(*) FROM art_dislikes
                             WHERE article_id = $1''', record.get('id')),
                     'commentaries': 0} for record in q]}


async def select_arts(request, conn, current_user, page, per_page, last):
    if permissions.BLOCK_ENTITY in current_user['permissions']:
        q = await conn.fetch(
            '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                      a.edited, a.state, a.commented, a.viewed,
                      accounts.ava_hash, users.username
                 FROM articles AS a, users, accounts
                 WHERE a.author_id = users.id
                   AND accounts.user_id = a.author_id
                   AND a.state IN ($1, $2, $3)
                 ORDER BY a.published DESC LIMIT $4 OFFSET $5''',
            status.pub, status.priv, status.hidden,
            per_page, per_page*(page-1))
    else:
        q = await conn.fetch(
            '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                      a.edited, a.state, a.commented, a.viewed,
                      accounts.ava_hash, users.username
                 FROM articles AS a, users, accounts
                 WHERE a.author_id = users.id
                   AND accounts.user_id = a.author_id
                   AND a.state IN ($1, $2)
                 ORDER BY a.published DESC LIMIT $3 OFFSET $4''',
            status.pub, status.priv, per_page, per_page*(page-1))
    if q:
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
                     'likes': await conn.fetchval(
                        'SELECT count(*) FROM art_likes WHERE article_id = $1',
                        record.get('id')),
                     'dislikes': await conn.fetchval(
                        '''SELECT count(*) FROM art_dislikes
                             WHERE article_id = $1''', record.get('id')),
                     'commentaries': 0} for record in q]}


async def select_blocked(request, conn, page, per_page, last):
    q = await conn.fetch(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                  a.edited, a.state, a.commented, a.viewed, acc.ava_hash,
                  u.username
             FROM articles AS a, accounts AS acc, users AS u
             WHERE a.author_id = u.id
               AND acc.user_id = a.author_id
               AND a.state = $1
             ORDER BY a.published DESC LIMIT $2 OFFSET $3''',
        status.mod, per_page, per_page*(page-1))
    if q:
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
                     'likes': await conn.fetchval(
                         '''SELECT count(*) FROM art_likes
                              WHERE article_id = $1''', record.get('id')),
                     'dislikes': await conn.fetchval(
                         '''SELECT count(*) FROM art_dislikes
                              WHERE article_id = $1''', record.get('id')),
                     'commentaries': 0} for record in q]}



async def select_banded(request, conn, cuid, page, per_page, last):
    q = await conn.fetch(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                  a.edited, a.state, a.commented, a.viewed,
                  acc.ava_hash, u.username
             FROM articles AS a, accounts AS acc, users AS u, followers AS f
             WHERE a.author_id = u.id
               AND a.author_id = f.author_id
               AND acc.user_id = a.author_id
               AND a.state IN ($1, $2, $3)
               AND f.follower_id = $4
             ORDER BY a.published DESC LIMIT $5 OFFSET $6''',
        status.pub, status.priv, status.hidden, cuid,
        per_page, per_page*(page-1))
    if q:
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
                     'likes': await conn.fetchval(
                         '''SELECT count(*) FROM art_likes
                              WHERE article_id = $1''', record.get('id')),
                     'dislikes': await conn.fetchval(
                         '''SELECT count(*) FROM art_dislikes
                              WHERE article_id = $1''', record.get('id')),
                     'commentaries': 0} for record in q]}


async def check_last_blocked(conn, page, per_page):
    return await parse_last_page(
        page, per_page, await conn.fetchval(
            'SELECT count(*) FROM articles WHERE state = $1', status.mod))


async def check_last_banded(conn, cuid, page, per_page):
    return await parse_last_page(page, per_page, await conn.fetchval(
        '''SELECT count(*) FROM articles AS a, followers AS f
             WHERE a.author_id = f.author_id
               AND a.state IN ($1, $2, $3)
               AND f.follower_id = $4''',
        status.pub, status.priv, status.hidden, cuid))


async def check_last_auth(conn, auth, current_user, page, per_page):
    if permissions.BLOCK_ENTITY in current_user['permissions'] or \
            current_user['id'] == auth['id']:
        q = await conn.fetchval(
            '''SELECT count(*) FROM articles
                 WHERE author_id = $1 AND state IN ($2, $3, $4)''',
            auth['id'], status.pub, status.priv, status.hidden)
    else:
        q = await conn.fetchval(
            '''SELECT count(*) FROM articles
                 WHERE author_id = $1 AND state IN ($2, $3)''',
            auth['id'], status.pub, status.priv)
    return await parse_last_page(page, per_page, q)


async def check_last_arts(conn, current_user, page, per_page):
    if permissions.BLOCK_ENTITY in current_user['permissions']:
        q = await conn.fetchval(
            'SELECT count(*) FROM articles WHERE state IN ($1, $2, $3)',
            status.pub, status.priv, status.hidden)
    else:
        q = await conn.fetchval(
            'SELECT count(*) FROM articles WHERE state IN ($1, $2)',
            status.pub, status.priv)
    return await parse_last_page(page, per_page, q)


async def check_art(request, conn, cu, slug, target):
    part = '''SELECT articles.id, articles.title, articles.slug,
                     articles.suffix, articles.html, articles.summary,
                     articles.meta, articles.published, articles.edited,
                     articles.state, articles.commented, articles.viewed,
                     articles.author_id, accounts.ava_hash, users.username,
                     users.permissions FROM articles, accounts, users'''
    if permissions.BLOCK_ENTITY in cu['permissions']:
        query = await conn.fetchrow(
            f'''{part} WHERE articles.slug = $1
                         AND articles.state IN ($2, $3, $4, $5)
                         AND users.id = articles.author_id
                         AND accounts.user_id = articles.author_id''',
            slug, status.pub, status.priv, status.hidden, status.mod)
    else:
        query = await conn.fetchrow(
            f'''{part} WHERE articles.slug = $1
                         AND articles.state IN ($2, $3, $4)
                         AND users.id = articles.author_id
                         AND accounts.user_id = articles.author_id''',
            slug, status.pub, status.priv, status.hidden)
    if query:
        target['id'] = query.get('id')
        target['title'] = query.get('title')
        target['title80'] = await parse_title(query.get('title'), 80)
        target['slug'] = query.get('slug')
        target['suffix'] = query.get('suffix')
        target['html'] = query.get('html')
        target['summary'] = query.get('summary')
        target['meta'] = query.get('meta')
        target['published'] = f'{query.get("published").isoformat()}Z' \
        if query.get('published') else None
        target['edited'] = f'{query.get("edited").isoformat()}Z'
        target['state'] = query.get('state')
        target['commented'] = query.get('commented')
        target['viewed'] = query.get('viewed')
        target['author'] = query.get('username')
        target['author_perms'] = query.get('permissions')
        target['author_id'] = query.get('author_id')
        target['ava'] = await get_ava_url(
            request, query.get('ava_hash'), size=88)
        target['likes'] = await conn.fetchval(
            'SELECT count(*) FROM art_likes WHERE article_id = $1',
            query.get('id'))
        target['dislikes'] = await conn.fetchval(
            'SELECT count(*) FROM art_dislikes WHERE article_id = $1',
            query.get('id'))
        target['commentaries'] = 0