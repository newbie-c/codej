import re

from starlette.responses import JSONResponse

from ..auth.attri import permissions
from ..auth.common import checkcu
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .pg import select_labels


async def set_labels(request):
    res = {'empty': True}
    d = await request.form()
    aid, labels = int(d.get('aid')), d.get('labels')
    current_user = await checkcu(request)
    if aid and current_user and \
            permissions.CREATE_ENTITY in current_user['permissions']:
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            '''SELECT id, author_id FROM articles
                 WHERE id = $1 AND author_id = $2''', aid, current_user['id'])
        if target:
            current = await select_labels(conn, aid)
            new = [l.strip().lower() for l in labels.split(',') if l]
            for each in new:
                if not re.match(r'^[a-zа-яё\d\-]{1,32}$', each):
                    res = {'empty': False, 'error': True}
                    await conn.close()
                    return JSONResponse(res)
            lq = 'SELECT id FROM labels WHERE label = $1'
            for each in current:
                if each not in new:
                    lid = await conn.fetchval(lq, each)
                    await conn.execute(
                        '''DELETE FROM als
                             WHERE article_id = $1 AND label_id = $2''',
                        aid, lid)
            for each in new:
                if each not in current:
                    lid = await conn.fetchval(lq, each)
                    if lid is None:
                        await conn.execute(
                            'INSERT INTO labels (label) VALUES ($1)', each)
                        lid = await conn.fetchval(lq, each)
                    await conn.execute(
                        '''INSERT INTO als (article_id, label_id)
                             VALUES ($1, $2)''', aid, lid)
            res = {'empty': False, 'error': False}
            await set_flashed(request, 'Метки установлены.')
        await conn.close()
    return JSONResponse(res)
