from starlette.responses import JSONResponse


async def show_art(request):
    slug = request.path_params.get('slug')
    return JSONResponse({'slug': slug, 'state': 'Not implemented yet.'})
