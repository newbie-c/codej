from starlette_wtf import StarletteForm
from wtforms.fields import (
    BooleanField, PasswordField, StringField, SubmitField)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class Passwords:
    password = PasswordField(
        'Новый пароль:',
        validators=[DataRequired(message='необходимо придумать пароль'),
                    EqualTo('confirmation', message='пароли не совпадают')])
    confirmation = PasswordField(
        'Повторите его:',
        validators=[DataRequired(message='необходимо повторить пароль')])


class CreatePassword(Passwords, StarletteForm):
    username = StringField(
        'Псевдоним:',
        validators=[
            DataRequired(message='необходимо ввести желаемый псевдоним'),
            Length(min=3, max=16, message='от 3-х до 16-ти символов'),
            Regexp(r'^[A-ZА-ЯЁa-zа-яё][A-ZА-ЯЁa-zа-яё0-9\-_.]{2,15}$',
                   message='латинские буквы, буквы русского алфавита, \
                            цифры, дефис, знак подчёркивания, точка, \
                            первый символ - латинская или русская буква, \
                            не более 16 символов')])
    submit = SubmitField('Создать пароль')


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
