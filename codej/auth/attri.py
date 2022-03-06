from collections import namedtuple

Perm = namedtuple(
        'Perm',
        ['CANNOT_LOG_IN',
         'READ_JOURNAL',
         'FOLLOW_USERS',
         'LIKE_DISLIKE',
         'SEND_PM',
         'WRITE_COMMENTARY',
         'CREATE_LINK_ALIAS',
         'CREATE_ENTITY',
         'BLOCK_ENTITY',
         'CHANGE_USER_ROLE',
         'UPLOAD_PICTURES',
         'MAKE_ANNOUNCEMENT',
         'SPECIAL_CASE',
         'ADMINISTER_SERVICE'])

permissions = Perm(
        CANNOT_LOG_IN='заблокирован',
        READ_JOURNAL='читать блоги',
        FOLLOW_USERS='создавать ленту',
        LIKE_DISLIKE='ставить лайки/дизлайки',
        SEND_PM='писать в приват',
        WRITE_COMMENTARY='комментировать блоги',
        CREATE_LINK_ALIAS='создавать алиасы для ссылок',
        CREATE_ENTITY='вести свой блог',
        BLOCK_ENTITY='литовать блоги и комментарии',
        CHANGE_USER_ROLE='назначать разрешения',
        UPLOAD_PICTURES='хранить изображения',
        MAKE_ANNOUNCEMENT='делать объявления',
        SPECIAL_CASE='размещать ссылки',
        ADMINISTER_SERVICE='без ограничений')

Group = namedtuple('Group', ['pariah',
                             'taciturn',
                             'commentator',
                             'blogger',
                             'curator',
                             'keeper',
                             'root'])

groups = Group(pariah='Изгои',
               taciturn='Читатели',
               commentator='Комментаторы',
               blogger='Писатели',
               curator='Модераторы',
               keeper='Хранители',
               root='Администраторы')

initials = {permissions.READ_JOURNAL: True,
            permissions.FOLLOW_USERS: True,
            permissions.LIKE_DISLIKE: True,
            permissions.SEND_PM: True,
            permissions.WRITE_COMMENTARY: True,
            permissions.CREATE_LINK_ALIAS: True,
            permissions.CREATE_ENTITY: True}

roots = [permission for permission in permissions
         if permission != permissions.CANNOT_LOG_IN]

average = {name.lower().replace('_', '-'): permission
        for name, permission in zip(permissions._fields, permissions)
        if permission != permissions.CANNOT_LOG_IN and
        permission != permissions.ADMINISTER_SERVICE}

curators = (permissions.CANNOT_LOG_IN,
            permissions.READ_JOURNAL,
            permissions.FOLLOW_USERS,
            permissions.LIKE_DISLIKE,
            permissions.SEND_PM,
            permissions.WRITE_COMMENTARY,
            permissions.CREATE_LINK_ALIAS,
            permissions.CREATE_ENTITY)

keepers = curators + (permissions.BLOCK_ENTITY, permissions.CHANGE_USER_ROLE)


async def fix_extra_permissions(user, current):
    if user['group'] == groups.keeper:
        return [permission for permission in current
                if permission not in keepers]
    if user['group'] == groups.curator:
        return [permission for permission in current
                if permission not in curators]
    return []
