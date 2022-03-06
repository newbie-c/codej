from ..auth.common import get_current_user
from ..common.pg import get_conn


async def notify_not_found_page(request, exc):
    conn = await get_conn(request.app.config)
    current_user = await get_current_user(request, conn)
    return request.app.jinja.TemplateResponse(
        'errors/error.html',
        {'reason': exc.detail,
         'request': request,
         'current_user': current_user,
         'error': exc.status_code},
        status_code=exc.status_code)


async def refuse_request(request, exc):
    conn = await get_conn(request.app.config)
    current_user = await get_current_user(request, conn)
    return request.app.jinja.TemplateResponse(
        'errors/error.html',
        {'reason': exc.detail,
         'request': request,
         'current_user': current_user,
         'error': exc.status_code},
        status_code=exc.status_code)


async def refuse_method(request, exc):
    conn = await get_conn(request.app.config)
    current_user = await get_current_user(request, conn)
    return request.app.jinja.TemplateResponse(
        'errors/error.html',
        {'reason': 'Метод не позволен.',
         'request': request,
         'current_user': current_user,
         'error': exc.status_code},
        status_code=exc.status_code)


async def handle_csrf_error(request, exc):
    conn = await get_conn(request.app.config)
    current_user = await get_current_user(request, conn)
    return request.app.jinja.TemplateResponse(
        'errors/error.html',
        {'reason': 'CSRF-брелок устарел или подделан.',
         'request': request,
         'current_user': current_user,
         'error': 'CSRF-error'},
        status_code=exc.status_code)
