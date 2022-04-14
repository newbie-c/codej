from ..auth.attri import groups, permissions
from ..common.avatar import get_ava_url


async def check_friends(conn, author, friend):
    if await conn.fetchrow(
            '''SELECT author_id, friend_id FROM friends
                 WHERE author_id = $1 AND friend_id = $2''', author, friend):
        return True
    return False


async def get_group(perms):
    if permissions.ADMINISTER_SERVICE in perms:
        return groups.root
    if permissions.CREATE_ENTITY in perms \
            and permissions.UPLOAD_PICTURES in perms \
            and permissions.MAKE_ANNOUNCEMENT in perms \
            and permissions.CHANGE_USER_ROLE in perms:
        return groups.keeper
    if permissions.BLOCK_ENTITY in perms:
        return groups.curator
    if permissions.CREATE_ENTITY in perms \
            or permissions.MAKE_ANNOUNCEMENT in perms \
            or permissions.UPLOAD_PICTURES in perms:
        return groups.blogger
    if permissions.LIKE_DISLIKE in perms \
            or permissions.WRITE_COMMENTARY in perms \
            or permissions.SEND_PM in perms:
        return groups.commentator
    if permissions.READ_JOURNAL in perms:
        return groups.taciturn
    if permissions.CANNOT_LOG_IN in perms:
        return groups.pariah


async def filter_target_user(request, conn):
    query = await conn.fetchrow(
        '''SELECT users.id AS uid,
                  users.username AS username,
                  users.registered AS registered,
                  users.last_visit AS last_visit,
                  users.permissions AS permissions,
                  users.description AS description,
                  accounts.address AS address,
                  accounts.ava_hash AS ava_hash
              FROM users, accounts WHERE users.username = $1
                AND users.id = accounts.user_id''',
        request.path_params['username'])
    if query:
        return {'uid': query.get('uid'),
                'username': query.get('username'),
                'group': await get_group(query.get('permissions')),
                'registered': query.get('registered').isoformat() + 'Z',
                'last_visit': query.get('last_visit').isoformat() + 'Z',
                'permissions': tuple(query.get('permissions')),
                'description': query.get('description'),
                'address': query.get('address'),
                'ava': await get_ava_url(
                    request, query.get('ava_hash'), size=160)}
