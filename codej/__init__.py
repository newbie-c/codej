import os

from starlette.applications import Starlette
from starlette.config import Config
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from .main.views import show_index, show_robots, show_favicon

base = os.path.dirname(__file__)
static = os.path.join(base, 'static')
settings = Config(os.path.join(os.path.dirname(base), '.env'))

app = Starlette(
    debug=settings.get('DEBUG', cast=bool),
    routes=[Route('/', show_index, name='index'),
            Route('/robots.txt', show_robots, name='robots'),
            Route('/favicon.ico', show_favicon, name='favicon'),
            Mount('/static',
                  app=StaticFiles(directory=static), name='static')])
app.config = settings
