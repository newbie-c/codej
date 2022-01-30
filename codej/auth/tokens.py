from datetime import datetime, timedelta

from jwt import encode as jwtencode
from jwt import PyJWTError, decode


async def check_token(request, conn):
    token = request.path_params['token']
    try:
        cache = decode(
            token, request.app.config.get('SECRET_KEY'), algorithms=['HS256'])
    except PyJWTError:
        return None
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
