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
    admin_pictures, admin_users, find_user, find_pic,
    rem_pic, set_index, set_init_perms, set_robots,
    set_service, show_log)
from .arts.views import (
    censor_art, follow_auth, show_art, show_arts,
    show_author, show_banded, show_blocked, show_labeled_arts,
    send_dislike, send_like, unfollow_auth)
from .auth.attri import groups, permissions
from .auth.tasks import check_swapped
from .auth.views import (
    change_email, change_password, create_password, get_password,
    login, logout, request_email, reset_password, update_captcha)
from .captcha.views import show_captcha
from .drafts.views import (
    change_title, check_par, create_draft, create_par,
    edit_par, edit_meta, edit_state, edit_sum,
    insert_par, rem_par, show_draft, show_drafts,
    show_labeled)
from .errors import (
    handle_csrf_error, notify_not_found_page,
    refuse_method, refuse_request)
from .labels.views import set_labels
from .main.views import (
    count_views, edit_desc, make_friend, jump,
    ping, show_favicon, show_index, show_picture,
    show_profile, show_robots, show_sitemap)
from .pictures.views import (
    change_state, check_pic, create_album, find_album,
    remove_pic, rename_album, show_album, show_album_stat,
    show_albums, show_pic_stat, show_user_stat)
from .public.views import show_blogs, show_topic

base = os.path.dirname(__file__)
static = os.path.join(base, 'static')
templates = os.path.join(base, 'templates')
settings = Config(os.path.join(os.path.dirname(base), '.env'))
try:
    from .addenv import SITE_NAME, SITE_DESCRIPTION
    if SITE_NAME:
        settings.file_values["SITE_NAME"] = SITE_NAME
    if SITE_DESCRIPTION:
        settings.file_values["SITE_DESCRIPTION"] = SITE_DESCRIPTION
except ModuleNotFoundError:
    pass


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
            Route('/sitemap.xml', show_sitemap, name='sitemap'),
            Route('/{suffix}', jump, name='jump'),
            Route('/ajax/count-views', count_views,
                  name='count-views', methods=['POST']),
            Route('/ajax/edit-desc', edit_desc,
                  name='edit-desc', methods=['POST']),
            Route('/ajax/make-friend', make_friend,
                  name="make-friend", methods=['POST']),
            Route('/ajax/ping', ping,
                  name='ping', methods=['POST']),
            Route('/picture/{suffix}', show_picture, name='show-picture'),
            Route('/society/{username}', show_profile,
                  name='profile', methods=['GET', 'POST']),
            Mount('/admin', name='admin', routes=[
                Route('/society', admin_users,
                      name='users', methods=['GET', 'POST']),
                Route('/pictures', admin_pictures, name='pictures'),
                Route('/settings', set_service, name='settings'),
                Route('/ajax/admin-perms', set_init_perms,
                      name='perms', methods=['POST']),
                Route('/ajax/find-user', find_user,
                      name='find-user', methods=['POST']),
                Route('/ajax/rem-pic', rem_pic,
                      name='rem-pic', methods=['POST']),
                Route('/ajax/find-pic', find_pic,
                      name='find-pic', methods=['POST']),
                Route('/ajax/set-robots', set_robots,
                      name='set-robots', methods=['POST']),
                Route('/ajax/set-index', set_index,
                      name='set-index', methods=['POST']),
                Route('/logs/{filename}', show_log, name='logs')]),
            Mount('/arts', name='arts', routes=[
                Route('/', show_arts, name='show-arts'),
                Route('/{slug}', show_art, name='show-art'),
                Route('/l/', show_banded, name='lenta'),
                Route('/a/{username}', show_author, name='show-auth'),
                Route('/b/', show_blocked, name='show-blocked'),
                Route('/t/{label}', show_labeled_arts, name='labeled-arts'),
                Route('/ajax/follow-auth', follow_auth,
                      name='follow-auth', methods=['POST']),
                Route('/ajax/unfollow-auth', unfollow_auth,
                      name='unfollow-auth', methods=['POST']),
                Route('/ajax/send-like', send_like,
                      name='send-like', methods=['POST']),
                Route('/ajax/send-dislike', send_dislike,
                      name='send-dislike', methods=['POST']),
                Route('/ajax/censor-art', censor_art,
                     name='censor-art', methods=['POST'])]),
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
            Mount('/drafts', name='drafts', routes=[
                Route('/', show_drafts, name='show-drafts'),
                Route('/{slug}', show_draft, name='show-draft'),
                Route('/t/{label}', show_labeled, name='show-labeled'),
                Route('/ajax/create', create_draft,
                      name='create', methods=['POST']),
                Route('/ajax/create-par', create_par,
                      name='create-par', methods=['POST']),
                Route('/ajax/check-par', check_par,
                      name='check-par', methods=['POST']),
                Route('/ajax/edit-par', edit_par,
                      name='edit-par', methods=['POST']),
                Route('/ajax/rem-par', rem_par,
                      name='rem-par', methods=['POST']),
                Route('/ajax/insert-par', insert_par,
                      name='insert-par', methods=['POST']),
                Route('/ajax/ch-title', change_title,
                      name='ch-title', methods=['POST']),
                Route('/ajax/edit-meta', edit_meta,
                      name='edit-meta', methods=['POST']),
                Route('/ajax/edit-sum', edit_sum,
                      name='edit-sum', methods=['POST']),
                Route('/ajax/edit-state', edit_state,
                      name='edit-state', methods=['POST'])]),
            Mount('/labels', name='labels', routes=[
                Route('/ajax/set-l', set_labels,
                      name='set-l', methods=['POST'])]),
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
            Mount('/public', name='public', routes=[
                Route('/', show_blogs, name='show-blogs'),
                Route('/{slug}', show_topic, name='show-topic')]),
            Mount('/static',
                  app=StaticFiles(directory=static), name='static')],
    on_startup=[run_before],
    middleware=middleware,
    exception_handlers=errs)
app.config = settings
app.jinja = J2Templates(directory=templates)
app.rc = aioredis.from_url(settings.get('REDI'), decode_responses=True)
