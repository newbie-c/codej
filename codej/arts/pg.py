from ..auth.attri import permissions
from ..common.aparsers import parse_last_page
from ..common.avatar import get_ava_url
from ..drafts.attri import status
from ..drafts.parse import parse_art_query, parse_arts_query


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


async def select_labeled_auth(
        request, conn, auth, cu, label, target, page, per_page, last):
    if permissions.BLOCK_ENTITY in cu['permissions'] or \
            auth['id'] == cu['id']:
        q = await conn.fetch(
            '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                      a.edited, a.state, a.commented, a.viewed,
                      accounts.ava_hash, users.username
                 FROM articles AS a, users, accounts, labels, als
                 WHERE a.author_id = users.id
                   AND a.author_id = $1
                   AND accounts.user_id = a.author_id
                   AND a.id = als.article_id
                   AND labels.label = $2
                   AND labels.id = als.label_id
                   AND a.state IN ($3, $4, $5)
                ORDER BY a.published ASC LIMIT $6 OFFSET $7''',
            auth['id'], label, status.pub, status.priv, status.hidden,
            per_page, per_page*(page-1))
    else:
        q = await conn.fetch(
            '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                      a.edited, a.state, a.commented, a.viewed,
                      accounts.ava_hash, users.username
                 FROM articles AS a, users, accounts, labels, als
                 WHERE a.author_id = users.id
                   AND a.author_id = $1
                   AND accounts.user_id = a.author_id
                   AND a.id = als.article_id
                   AND labels.label = $2
                   AND labels.id = als.label_id
                   AND a.state IN ($3, $4)
                ORDER BY a.published ASC LIMIT $5 OFFSET $6''',
            auth['id'], label, status.pub, status.priv,
            per_page, per_page*(page-1))
    if q:
        await parse_arts_query(request, conn, q, target, page, last)


async def select_auth(request, conn, auth, cu, target, page, per_page, last):
    if permissions.BLOCK_ENTITY in cu['permissions'] or \
            auth['id'] == cu['id']:
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
        await parse_arts_query(request, conn, q, target, page, last)


async def select_labeled_arts(
        request, conn, cu, label, target, page, per_page, last):
    if permissions.BLOCK_ENTITY in cu['permissions']:
        q = await conn.fetch(
            '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                      a.edited, a.state, a.commented, a.viewed,
                      accounts.ava_hash, users.username
                 FROM articles AS a, users, accounts, labels, als
                 WHERE a.author_id = users.id
                   AND accounts.user_id = a.author_id
                   AND a.id = als.article_id
                   AND labels.label = $1
                   AND labels.id = als.label_id
                   AND a.state IN ($2, $3, $4)
                 ORDER BY a.published ASC LIMIT $5 OFFSET $6''',
            label, status.pub, status.priv, status.hidden,
            per_page, per_page*(page-1))
    else:
        q = await conn.fetch(
            '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                      a.edited, a.state, a.commented, a.viewed,
                      accounts.ava_hash, users.username
                 FROM articles AS a, users, accounts, labels, als
                 WHERE a.author_id = users.id
                   AND accounts.user_id = a.author_id
                   AND a.id = als.article_id
                   AND labels.label = $1
                   AND labels.id = als.label_id
                   AND a.state IN ($2, $3)
                 ORDER BY a.published ASC LIMIT $4 OFFSET $5''',
            label, status.pub, status.priv, per_page, per_page*(page-1))
    if q:
        await parse_arts_query(request, conn, q, target, page, last)


async def select_arts(request, conn, cu, target, page, per_page, last):
    if permissions.BLOCK_ENTITY in cu['permissions']:
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
        await parse_arts_query(request, conn, q, target, page, last)


async def select_blocked(request, conn, target, page, per_page, last):
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
        await parse_arts_query(request, conn, q, target, page, last)


async def select_banded(request, conn, cuid, target, page, per_page, last):
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
        await parse_arts_query(request, conn, q, target, page, last)


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


async def check_last_labeled_auth(
        conn, author, current_user, label, page, per_page):
    if permissions.BLOCK_ENTITY in current_user['permissions'] or \
            current_user['id'] == author['id']:
        q = await conn.fetchval(
            '''SELECT count(*) FROM articles, labels, als
                 WHERE articles.author_id = $1
                   AND articles.id = als.article_id
                   AND labels.label = $2
                   AND labels.id = als.label_id
                   AND articles.state IN ($3, $4, $5)''',
            author['id'], label, status.pub, status.priv, status.hidden)
    else:
        q = await conn.fetchval(
            '''SELECT count(*) FROM articles, labels, als
                 WHERE articles.author_id = $1
                   AND articles.id = als.article_id
                   AND labels.label = $2
                   AND labels.id = als.label_id
                   AND articles.state IN ($3, $4)''',
            author['id'], label, status.pub, status.priv)
    return await parse_last_page(page, per_page, q)


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


async def check_last_labeled_arts(conn, current_user, label, page, per_page):
    if permissions.BLOCK_ENTITY in current_user['permissions']:
        q = await conn.fetchval(
            '''SELECT count(*) FROM articles, labels, als
                 WHERE articles.author_id = als.article_id
                   AND labels.label = $1
                   AND labels.id = als.label_id
                   AND articles.state IN ($2, $3, $4)''',
            label, status.pub, status.priv, status.hidden)
    else:
        q = await conn.fetchval(
            '''SELECT count(*) FROM articles, labels, als
                 WHERE articles.author_id = als.article_id
                   AND labels.label = $1
                   AND labels.id = als.label_id
                   AND articles.state IN ($2, $3)''',
            label, status.pub, status.priv)
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
                         AND articles.state != $2
                         AND users.id = articles.author_id
                         AND accounts.user_id = articles.author_id''',
            slug, status.draft)
    else:
        query = await conn.fetchrow(
            f'''{part} WHERE articles.slug = $1
                         AND articles.state != $2
                         AND articles.state != $3
                         AND users.id = articles.author_id
                         AND accounts.user_id = articles.author_id''',
            slug, status.mod, status.draft)
    if query:
        await parse_art_query(request, conn, query, target)
