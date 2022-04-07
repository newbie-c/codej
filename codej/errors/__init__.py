from ..auth.common import checkcu
from ..common.pg import get_conn


async def notify_not_found_page(request, exc):
    current_user = await checkcu(request)
    return request.app.jinja.TemplateResponse(
        'errors/error.html',
        {'reason': exc.detail,
         'request': request,
         'current_user': current_user,
         'error': exc.status_code},
        status_code=exc.status_code)


async def refuse_request(request, exc):
    current_user = await checkcu(request)
    return request.app.jinja.TemplateResponse(
        'errors/error.html',
        {'reason': exc.detail,
         'request': request,
         'current_user': current_user,
         'error': exc.status_code},
        status_code=exc.status_code)


async def refuse_method(request, exc):
    current_user = await checkcu(request)
    return request.app.jinja.TemplateResponse(
        'errors/error.html',
        {'reason': 'Метод не позволен.',
         'request': request,
         'current_user': current_user,
         'error': exc.status_code},
        status_code=exc.status_code)


async def handle_csrf_error(request, exc):
    current_user = await checkcu(request)
    return request.app.jinja.TemplateResponse(
        'errors/error.html',
        {'reason': 'CSRF-брелок устарел или подделан.',
         'request': request,
         'current_user': current_user,
         'error': 'CSRF-error'},
        status_code=exc.status_code)
