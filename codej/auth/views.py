from starlette_wtf import csrf_protect

from ..common.flashed import get_flashed, set_flashed


@csrf_protect
async def login(request):
    await set_flashed(request, 'First message.')
    await set_flashed(request, 'Second message.')
    await set_flashed(request, 'Third message.')
    return request.app.jinja.TemplateResponse(
        'auth/login.html',
        {'request': request,
         'flashed': await get_flashed(request)})
