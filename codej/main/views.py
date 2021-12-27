import os

from starlette.responses import FileResponse, PlainTextResponse

robots = """User-agent: *
Disallow: /
"""


async def show_index(request):
   return request.app.jinja.TemplateResponse(
          'main/index.html',
          {'request': request})


async def show_robots(request):
    if request.method == 'GET':
        return PlainTextResponse(robots)


async def show_favicon(request):
    if request.method == 'GET':
        base = os.path.dirname(os.path.dirname(__file__))
        return FileResponse(
            os.path.join(base, 'static', 'images', 'favicon.ico'))
