from datetime import datetime, timedelta

from jwt import encode as jwtencode
from jwt import PyJWTError, decode


async def check_token(request, conn, wide=False):
    token = request.path_params['token']
    try:
        cache = decode(
            token, request.app.config.get('SECRET_KEY'), algorithms=['HS256'])
    except PyJWTError:
        return None
    if wide:
        return await conn.fetchrow(
            '''SELECT accounts.id, accounts.user_id, accounts.requested,
                      accounts.swap, users.username, users.last_visit
                 FROM accounts, users
                 WHERE accounts.id = $1 AND accounts.user_id = users.id''',
            cache['aid'])
    return await conn.fetchrow(
        'SELECT id, address, user_id FROM accounts WHERE id = $1',
        cache['aid'])


async def get_request_token(request, aid):
    delta = timedelta(
        seconds = round(
            request.app.config.get('TOKEN_LENGTH', cast=float) * 3600))
    cache = {'aid': aid, 'exp': datetime.utcnow() + delta}
    return jwtencode(
        cache, request.app.config.get('SECRET_KEY'), algorithm='HS256')
