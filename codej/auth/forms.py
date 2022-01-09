from starlette_wtf import StarletteForm
from wtforms.fields import (
    BooleanField, PasswordField, StringField, SubmitField)
from wtforms.validators import DataRequired


class LoginForm(StarletteForm):
    login = StringField(
        'Логин:',
        validators=[DataRequired(
            message='Введите псевдоним или адрес эл.почты')])
    password = PasswordField(
        'Пароль:',
        validators=[DataRequired(message='необходимо ввести пароль')])
    remember_me = BooleanField('Хранить сессию 30 дней')
    captcha = StringField(
        'Код с картинки:',
        validators=[DataRequired(message='необходимо ввести код с картинки')])
    suffix = StringField(
        'Суффикс:',
        validators=[DataRequired(message='обязательное поле')])
    submit = SubmitField('Войти в сервис')
