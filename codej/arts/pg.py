from ..common.aparsers import parse_title
from ..common.avatar import get_ava_url
from ..drafts.attri import status


async def check_art(request, conn, slug):
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
               AND articles.state IN ($2, $3, $4)
               AND users.id = articles.author_id
               AND accounts.user_id = articles.author_id''',
        slug, status.pub, status.priv, status.hidden)
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
