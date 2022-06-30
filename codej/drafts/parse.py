from ..common.aparsers import iter_pages, parse_title
from ..common.avatar import get_ava_url


async def parse_arts_query(request, conn, query, target, page, last):
    target['page'] = page
    target['next'] = page + 1 if page + 1 <= last else None
    target['prev'] = page - 1 or None
    target['pages'] = await iter_pages(page, last)
    target['articles'] = [
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
         'commentaries': 0} for record in query]


async def parse_art_query(request, conn, query, target):
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
