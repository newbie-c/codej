import asyncio
import getpass
import re

from validate_email import validate_email

from codej import settings
from codej.auth.attri import roots
from codej.auth.query import (
        check_address, check_username, create_user, insert_permissions)

USERNAME = 'Enter your username: '
MESSAGE = '''Username must be from 3 to 16 symbols
(latin letters,
russian letters including ё,
numbers, dots, hyphens, underscores)
and start with any letter (latin or russian).
'''
EMAIL = 'Enter your email address: '
PASSWORD = 'Enter your password: '


def get_username():
    pattern = re.compile(r'^[A-ZА-ЯЁa-zа-яё][A-ZА-ЯЁa-zа-яё0-9\-_.]{2,15}$')
    username = input(USERNAME)
    while True:
        if not pattern.match(username):
            print(MESSAGE)
            username = input(USERNAME)
            continue
        if asyncio.run(check_username(settings, username)):
            print('This name is already registered. Try again.\n')
            username = input(USERNAME)
            continue
        return username


def get_email():
    address = input(EMAIL)
    while True:
        if not validate_email(address):
            print('This is not a valid email address.\n')
            address = input(EMAIL)
            continue
        if asyncio.run(check_address(settings, address)):
            print('This email address cannot be registered. Try another.\n')
            address = input(EMAIL)
            continue
        return address


def get_password():
    phrase = getpass.getpass(PASSWORD)
    while True:
        confirm = getpass.getpass('Confirm the password: ')
        if confirm != phrase:
            print('Passwords must match!\n')
            phrase = getpass.getpass(PASSWORD)
            continue
        return phrase


async def main(username, address, pwd):
    await insert_permissions(settings)
    await create_user(settings, username, address, pwd, roots)


if __name__ == '__main__':
    asyncio.run(main(
        get_username(), get_email(), get_password()))
