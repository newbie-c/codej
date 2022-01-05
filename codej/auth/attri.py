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

initials = {permissions.READ_JOURNAL: True,
            permissions.FOLLOW_USERS: True,
            permissions.LIKE_DISLIKE: True,
            permissions.SEND_PM: True,
            permissions.WRITE_COMMENTARY: True,
            permissions.CREATE_LINK_ALIAS: True,
            permissions.CREATE_ENTITY: True}

roots = [permission for permission in permissions
         if permission != permissions.CANNOT_LOG_IN]
