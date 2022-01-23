from starlette.responses import Response
from starlette.exceptions import HTTPException

from ..common.pg import get_conn


async def show_captcha(request):
    conn = await get_conn(request.app.config)
    res = await conn.fetchrow(
        'SELECT * FROM captchas WHERE suffix = $1',
        request.path_params.get('suffix'))
    await conn.close()
    if res is None:
        raise HTTPException(status_code=404, detail='Страница не найдена')
    response = Response(res.get('picture'), media_type='image/jpeg')
    response.headers.append(
        'cache-control',
        'max-age=0, no-store, no-cache, must-revalidate')
    return response
