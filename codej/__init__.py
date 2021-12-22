import os

from starlette.applications import Starlette
from starlette.config import Config
from starlette.routing import Route

from .main.views import show_index

base = os.path.dirname(__file__)
settings = Config(os.path.join(os.path.dirname(base), '.env'))

app = Starlette(
    debug=settings.get('DEBUG', cast=bool),
    routes=[Route('/', show_index, name='index')])
app.config = settings
