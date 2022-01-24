from starlette_wtf import StarletteForm
from wtforms.fields import (
    BooleanField, PasswordField, StringField, SubmitField)
from wtforms.validators import DataRequired, Email, Length


class GetPassword(StarletteForm):
    address = StringField(
        'Адрес эл.почты:',
        validators=[DataRequired(message='необходима эл.почта'),
                    Email(message='нужен адрес электронной почты'),
                    Length(
                        max=128,
                        message='максимальная длина адреса - 128 символов')])
    captcha = StringField(
        'Код с картинки:',
        validators=[DataRequired(message='необходимо ввести код с картинки')])
    suffix = StringField(
        'Суффикс:',
        validators=[DataRequired(message='обязательное поле')])
    submit = SubmitField('Получить пароль')


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
