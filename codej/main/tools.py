from ..auth.attri import permissions
from ..pictures.attri import status
from .pg import check_friends


async def check_state(conn, target, current_user):
    if target['state'] == status.pub:
        return True
    elif target['state'] == status.priv:
        if current_user:
            return True
    elif target['state'] == status.ffo:
        if current_user and current_user['id'] == target['author_id']:
            return True
        if current_user and \
                permissions.ADMINISTER_SERVICE in current_user['permissions']:
            return True
        if current_user and \
                await check_friends(
                        conn, target['author_id'], current_user['id']):
            return True
    return False
