import os

from starlette.responses import FileResponse, HTMLResponse, PlainTextResponse

html = '''<!DOCTYPE html>
<html>
  <head>
    <title>CodeJ</title>
    <link rel="icon" href="/favicon.ico" type="image/vnd.microsoft.icon">
  </head>
  <body>
    <p>Сайт в стадии разработки, попробуйте зайти позже.</p>
  </body>
</html>
'''
robots = """User-agent: *
Disallow: /
"""


async def show_index(request):
   return HTMLResponse(html)


async def show_robots(request):
    if request.method == 'GET':
        return PlainTextResponse(robots)


async def show_favicon(request):
    if request.method == 'GET':
        base = os.path.dirname(os.path.dirname(__file__))
        return FileResponse(
            os.path.join(base, 'static', 'images', 'favicon.ico'))
