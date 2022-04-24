import os

import aioredis
import jinja2
import typing

from starlette.applications import Starlette
from starlette.config import Config
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette_wtf import CSRFProtectMiddleware, CSRFError
from webassets import Environment as AssetsEnvironment
from webassets.ext.jinja2 import assets

from .admin.views import (
    admin_users, find_user, set_init_perms, set_service, show_log)
from .auth.attri import groups, permissions
from .auth.tasks import check_swapped
from .auth.views import (
    change_email, change_password, create_password, get_password,
    login, logout, request_email, reset_password, update_captcha)
from .captcha.views import show_captcha
from .errors import (
    handle_csrf_error, notify_not_found_page,
    refuse_method, refuse_request)
from .main.views import (
    make_friend, show_index, show_picture, show_profile,
    show_robots, show_favicon)
from .pictures.views import (
    change_state, check_pic, create_album, find_album,
    remove_pic, rename_album, show_album, show_album_stat,
    show_albums, show_pic_stat, show_user_stat)

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
        env.globals["permissions"] = permissions
        env.globals["groups"] = groups
        return env


async def run_before():
    await check_swapped(settings)


middleware = [
    Middleware(
        SessionMiddleware,
        secret_key=settings.get('SECRET_KEY'),
        max_age=settings.get('SESSION_LIFETIME', cast=int)),
    Middleware(CSRFProtectMiddleware, csrf_secret=settings.get('SECRET_KEY'))]
errs = {403: refuse_request,
        404: notify_not_found_page,
        405: refuse_method,
        CSRFError: handle_csrf_error}
app = Starlette(
    debug=settings.get('DEBUG', cast=bool),
    routes=[Route('/', show_index, name='index'),
            Route('/robots.txt', show_robots, name='robots'),
            Route('/favicon.ico', show_favicon, name='favicon'),
            Route('/ajax/make-friend', make_friend,
                  name="make-friend", methods=['POST']),
            Route('/picture/{suffix}', show_picture, name='show-picture'),
            Route('/society/{username}', show_profile,
                  name='profile', methods=['GET', 'POST']),
            Mount('/admin', name='admin', routes=[
                Route('/society', admin_users,
                      name='users', methods=['GET', 'POST']),
                Route('/settings', set_service, name='settings'),
                Route('/ajax/admin-perms', set_init_perms,
                      name='perms', methods=['POST']),
                Route('/ajax/find-user', find_user,
                      name='find-user', methods=['POST']),
                Route('/logs/{filename}', show_log, name='logs')]),
            Mount('/auth', name='auth', routes=[
                Route('/login', login,
                      name='login', methods=['GET', 'POST']),
                Route('/logout', logout, name='logout'),
                Route('/get-password', get_password,
                      name='get-password', methods=['GET', 'POST']),
                Route('/create-password/{token}', create_password,
                      name='create-password', methods=['GET', 'POST']),
                Route('/reset-password/{token}', reset_password,
                      name='reset-password', methods=['GET', 'POST']),
                Route('/change-password', change_password,
                      name='change-password', methods=['GET', 'POST']),
                Route('/request-email', request_email,
                      name='request-email', methods=['GET', 'POST']),
                Route('/change-email/{token}', change_email,
                      name='change-email', methods=['GET', 'POST']),
                Route('/ajax/upd-captcha', update_captcha,
                      name='upd-captcha', methods=['POST'])]),
            Mount('/captcha', name='captcha', routes=[
                Route('/{suffix}', show_captcha, name='captcha')]),
            Mount('/pictures', name='pictures', routes=[
                Route('/', show_albums,
                      name='show-albums', methods=['GET', 'POST']),
                Route('/{suffix}', show_album,
                      name='show-album', methods=['GET', 'POST']),
                Route('/ajax/create-album', create_album,
                      name='create-album', methods=['POST']),
                Route('/ajax/check-pic', check_pic,
                      name='check-pic', methods=['POST']),
                Route('/ajax/change-state', change_state,
                      name='change-state', methods=['POST']),
                Route('/ajax/rename-album', rename_album,
                      name='rename-album', methods=['POST']),
                Route('/ajax/show-album-stat', show_album_stat,
                      name='show-album-stat', methods=['POST']),
                Route('/ajax/show-user-stat', show_user_stat,
                      name='show-user-stat', methods=['POST']),
                Route('/ajax/show-pic-stat', show_pic_stat,
                      name='show-pic-stat', methods=['POST']),
                Route('/ajax/find-album', find_album,
                      name='find-album', methods=['POST']),
                Route('/ajax/remove-pic', remove_pic,
                      name='remove-pic', methods=['POST'])]),
            Mount('/static',
                  app=StaticFiles(directory=static), name='static')],
    on_startup=[run_before],
    middleware=middleware,
    exception_handlers=errs)
app.config = settings
app.jinja = J2Templates(directory=templates)
app.rc = aioredis.from_url(settings.get('REDI'), decode_responses=True)
