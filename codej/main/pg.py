from ..common.avatar import get_ava_url


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
                'registered': query.get('registered').isoformat() + 'Z',
                'last_visit': query.get('last_visit').isoformat() + 'Z',
                'permissions': tuple(query.get('permissions')),
                'description': query.get('description'),
                'address': query.get('address'),
                'ava': await get_ava_url(
                    request, query.get('ava_hash'), size=160)}
