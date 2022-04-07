import asyncio

from datetime import datetime

from ..common.avatar import get_ava_url
from ..common.flashed import set_flashed
from ..main.pg import get_group
from .attri import permissions
from .tasks import ping_user


async def checkcu(request):
    uid_ = request.session.get('_uid')
    if uid_:
        uid = await request.app.rc.get(uid_) or '0'
        if uid := int(uid):
            query = await request.app.rc.hgetall(f'data:{uid}')
            if permissions.CANNOT_LOG_IN in query.get('permissions'):
                await request.app.rc.delete(uid_)
                await request.app.rc.delete(f'data:{uid}')
                del request.session['_uid']
                await set_flashed(
                    request, 'Ваше присутствие в сервисе нежелательно.')
                return None
            asyncio.ensure_future(
                ping_user(request, datetime.utcnow(), uid))
            return {'id': int(query.get('id')),
                    'username': query.get('username'),
                    'group': await get_group(query.get('permissions')),
                    'registered': query.get('registered'),
                    'permissions': query.get('permissions').split(','),
                    'ava': await get_ava_url(
                        request, query.get('ava'), size=22)}
        else:
            del request.session['_uid']


async def get_current_user(request, conn):
    uid_ = request.session.get('_uid')
    if uid_:
        uid = await request.app.rc.get(uid_) or '0'
        if uid := int(uid):
            query = await conn.fetchrow(
                '''SELECT users.id AS id,
                          users.username AS username,
                          users.registered AS registered,
                          users.permissions AS permissions,
                          accounts.ava_hash AS ava
                   FROM users, accounts WHERE users.id = accounts.user_id
                     AND users.id = $1''', int(uid))
            if permissions.CANNOT_LOG_IN in query.get('permissions'):
                await request.app.rc.delete(uid_)
                del request.session['_uid']
                await set_flashed(
                        request, 'Ваше присутствие в сервисе нежелательно.')
                return None
            asyncio.ensure_future(
                ping_user(request, datetime.utcnow(), uid))
            return {'id': query.get('id'),
                    'username': query.get('username'),
                    'group': await get_group(query.get('permissions')),
                    'registered': query.get('registered'),
                    'permissions': query.get('permissions'),
                    'ava': await get_ava_url(
                        request, query.get('ava'), size=22)}
        else:
            del request.session['_uid']

