import os

import jinja2
import typing

from starlette.applications import Starlette
from starlette.config import Config
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from webassets import Environment as AssetsEnvironment
from webassets.ext.jinja2 import assets

from .captcha.views import show_captcha
from .errors import (
        notify_not_found_page, refuse_method, refuse_request)
from .main.views import show_index, show_robots, show_favicon

base = os.path.dirname(__file__)
static = os.path.join(base, 'static')
templates = os.path.join(base, 'templates')
settings = Config(os.path.join(os.path.dirname(base), '.env'))


class J2Templates(Jinja2Templates):
    def _create_env(self, directory: str) -> "jinja2.Environment":
        @jinja2.pass_context
        def url_for(
                context: dict, name: str, **path_params: typing.Any) -> str:
            request = context["request"]
            return request.url_for(name, **path_params)

        loader = jinja2.FileSystemLoader(directory)
        assets_env = AssetsEnvironment(static, '/static')
        assets_env.debug = settings.get('ASSETS_DEBUG', bool)
        env = jinja2.Environment(
            loader=loader, autoescape=True, extensions=[assets])
        env.assets_environment = assets_env
        env.globals["url_for"] = url_for
        return env


middleware = [
    Middleware(
        SessionMiddleware,
        secret_key=settings.get('SECRET_KEY'),
        max_age=settings.get('SESSION_LIFETIME', cast=int))]
errs = {403: refuse_request,
        404: notify_not_found_page,
        405: refuse_method}
app = Starlette(
    debug=settings.get('DEBUG', cast=bool),
    routes=[Route('/', show_index, name='index'),
            Route('/robots.txt', show_robots, name='robots'),
            Route('/favicon.ico', show_favicon, name='favicon'),
            Mount('/captcha', routes=[
                Route('/{suffix}', show_captcha, name='captcha')]),
            Mount('/static',
                  app=StaticFiles(directory=static), name='static')],
    middleware=middleware,
    exception_handlers=errs)
app.config = settings
app.jinja = J2Templates(directory=templates)
