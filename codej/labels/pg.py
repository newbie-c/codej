async def select_labels(conn, aid):
    return [label.get('label') for label in await conn.fetch(
        '''SELECT labels.label FROM articles, labels, als
             WHERE articles.id = als.article_id
               AND labels.id = als.label_id
               AND articles.id = $1''', aid)]
