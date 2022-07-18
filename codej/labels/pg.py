from ..common.aparsers import iter_pages, parse_last_page
from ..drafts.attri import status

public = '''SELECT count(*) FROM articles AS a, als
              WHERE a.author_id IS NOT NULL
                AND als.article_id = a.id
                AND als.label_id = $1
                AND a.state IN ($2, $3)'''

hidden = '''SELECT count(*) FROM articles AS a, als
              WHERE a.author_id IS NOT NULL
                AND als.article_id = a.id
                AND als.label_id = $1
                AND a.state = $2'''

mod = '''SELECT count(*) FROM articles AS a, als
           WHERE a.author_id IS NOT NULL
             AND als.article_id = a.id
             AND als.label_id = $1
             AND a.state = $2'''


async def select_found(conn, target, value):
    q = await conn.fetch(
        '''SELECT DISTINCT l.id AS lid, l.label AS label
             FROM labels AS l, articles AS a, als
               WHERE a.id = als.article_id
                 AND l.id = als.label_id
                 AND a.author_id IS NOT NULL
                 AND a.state != $1
                 AND l.label LIKE $2
             ORDER BY l.label ASC''',
        status.draft, f'{value}%')
    if q:
        target['labels'] = [{
            'id': record.get('lid'),
            'label': record.get('label'),
            'public': await conn.fetchval(
                 public, record.get('lid'), status.pub, status.priv),
            'hidden': await conn.fetchval(
                 hidden, record.get('lid'), status.hidden),
            'mod': await conn.fetchval(
                 mod, record.get('lid'), status.mod)} for record in q]


async def select_ls(conn, target, page, per_page, last):
    q = await conn.fetch(
        '''SELECT DISTINCT l.id AS lid, l.label AS label
             FROM labels AS l, articles AS a, als
               WHERE a.id = als.article_id
                 AND l.id = als.label_id
                 AND a.state != $1
                 AND a.author_id IS NOT NULL
              ORDER BY l.label ASC LIMIT $2 OFFSET $3''',
        status.draft, per_page, per_page*(page-1))
    if q:
        target['page'] = page
        target['next'] = page + 1 if page + 1 <= last else None
        target['prev'] = page - 1 or None
        target['pages'] = await iter_pages(page, last)
        target['labels'] = [
            {'id': record.get('lid'),
             'label': record.get('label'),
             'public': await conn.fetchval(
                 public, record.get('lid'), status.pub, status.priv),
             'hidden': await conn.fetchval(
                 hidden, record.get('lid'), status.hidden),
             'mod': await conn.fetchval(
                 mod, record.get('lid'), status.mod)} for record in q]


async def check_last(conn, page, per_page):
    return await parse_last_page(
        page, per_page, await conn.fetchval(
            '''SELECT count(*) FROM
                 (SELECT DISTINCT l.id AS lid, l.label AS label
                    FROM labels AS l, articles AS a, als
                      WHERE a.id = als.article_id
                        AND l.id = als.label_id
                        AND a.state != $1
                        AND a.author_id IS NOT NULL) AS active''',
            status.draft))


async def select_labels(conn, aid):
    return [label.get('label') for label in await conn.fetch(
        '''SELECT labels.label FROM articles, labels, als
             WHERE articles.id = als.article_id
               AND labels.id = als.label_id
               AND articles.id = $1''', aid)]
