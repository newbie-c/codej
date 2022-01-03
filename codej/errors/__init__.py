async def notify_not_found_page(request, exc):
    return request.app.jinja.TemplateResponse(
        'errors/error.html',
        {'reason': 'Такой страницы у нас нет.',
         'request': request,
         'error': exc.status_code},
        status_code=exc.status_code)


async def refuse_request(request, exc):
    return request.app.jinja.TemplateResponse(
        'errors/error.html',
        {'reason': 'Доступ ограничен.',
         'request': request,
         'error': exc.status_code},
        status_code=exc.status_code)


async def refuse_method(request, exc):
    return request.app.jinja.TemplateResponse(
        'errors/error.html',
        {'reason': 'Метод не позволен.',
         'request': request,
         'error': exc.status_code},
        status_code=exc.status_code)
