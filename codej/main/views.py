from starlette.responses import HTMLResponse

html = """<!DOCTYPE html>
<html>
  <head>
    <title>CodeJ</title>
  </head>
  <body>
    <p>Сайт в стадии разработки, попробуйте зайти позже.</p>
  </body>
</html>
"""


async def show_index(request):
   return HTMLResponse(html)
