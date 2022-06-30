from ..common.aparsers import iter_pages, parse_last_page, parse_title
from ..common.avatar import get_ava_url
from ..drafts.attri import status
from ..drafts.parse import parse_art_query


async def select_pub(request, conn, page, per_page, last):
    q = await conn.fetch(
        '''SELECT users.id,
                  users.username,
                  users.registered,
                  users.description,
                  users.last_published,
                  accounts.ava_hash
             FROM users, accounts
             WHERE users.last_published IS NOT null
               AND users.description IS NOT null
               AND accounts.user_id = users.id
             ORDER BY users.last_published DESC LIMIT $1 OFFSET $2''',
        per_page, per_page*(page-1))
    if q:
        return {'page': page,
                'next': page + 1 if page + 1 <= last else None,
                'prev': page - 1 or None,
                'pages': await iter_pages(page, last),
                'blogs': [
                    {'id': record.get('id'),
                     'username': record.get('username'),
                     'registered': f'{record.get("registered").isoformat()}Z',
                     'description': record.get('description'),
                     'last_pub':
                     f'{record.get("last_published").isoformat()}Z',
                     'ava': await get_ava_url(
                         request, record.get('ava_hash'), size=88)}
                     for record in q]}


async def check_last_pub(conn, page, per_page):
    return await parse_last_page(page, per_page, await conn.fetchval(
        '''SELECT count(*) FROM users
             WHERE last_published IS NOT null
               AND description IS NOT null'''))


async def check_topic(request, conn, slug, target):
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
               AND articles.state = $2
               AND users.id = articles.author_id
               AND accounts.user_id = articles.author_id''',
        slug, status.pub)
    if query:
        await parse_art_query(request, conn, query, target)
