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


class ChangePassword(Passwords, StarletteForm):
    current = PasswordField(
        'Текущий пароль:',
        validators=[DataRequired(message='необходимо ввести текущий пароль')])
    submit = SubmitField('Сменить пароль')


class Address:
    address = StringField(
        'Адрес эл.почты:',
        validators=[DataRequired(message='необходима эл.почта'),
                    Email(message='нужен адрес электронной почты'),
                    Length(
                        max=128,
                        message='максимальная длина адреса - 128 символов')])


class ResetPassword(Passwords, Address, StarletteForm):
    submit = SubmitField('Обновить пароль')


class Username:
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


class CreatePassword(Username, Passwords, StarletteForm):
    submit = SubmitField('Создать пароль')


class GetPassword(Address, StarletteForm):
    captcha = StringField(
        'Код с картинки:',
        validators=[DataRequired(message='необходимо ввести код с картинки')])
    suffix = StringField(
        'Суффикс:',
        validators=[DataRequired(message='обязательное поле')])
    submit = SubmitField('Получить пароль')


class Password:
    password = PasswordField(
        'Пароль:',
        validators=[DataRequired(message='необходимо ввести пароль')])


class RequestEmail(Address, Password, StarletteForm):
    submit = SubmitField('Отправить запрос')


class LoginForm(Password, StarletteForm):
    login = StringField(
        'Логин:',
        validators=[DataRequired(
            message='Введите псевдоним или адрес эл.почты')])
    remember_me = BooleanField('Хранить сессию 30 дней')
    captcha = StringField(
        'Код с картинки:',
        validators=[DataRequired(message='необходимо ввести код с картинки')])
    suffix = StringField(
        'Суффикс:',
        validators=[DataRequired(message='обязательное поле')])
    submit = SubmitField('Войти в сервис')
