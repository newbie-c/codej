from datetime import datetime, timedelta

from jwt import encode as jwtencode


async def get_request_token(request, aid):
    delta = timedelta(
        seconds = round(
            request.app.config.get('TOKEN_LENGTH', cast=float) * 3600))
    cache = {'aid': aid, 'exp': datetime.utcnow() + delta}
    return jwtencode(
        cache, request.app.config.get('SECRET_KEY'), algorithm='HS256')
