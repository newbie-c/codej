async def define_target_url(request, account, token):
    if account.get('user_id'):
        return request.url_for('auth:reset-password', token=token)
    return request.url_for('auth:create-password', token=token)
