from starlette_wtf import StarletteForm
from wtforms.fields import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

from ..auth.forms import Address, Passwords, Username


class CreateUser(Username, Address, Passwords, StarletteForm):
    submit = SubmitField('Создать аккаунт')
