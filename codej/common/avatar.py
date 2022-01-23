async def get_ava_url(request, hash, size=100, default='mm', rating='g'):
    return '{0}/{1}?s={2}&d={3}&r={4}'.format(
        request.app.config.get('GRAVATAR'), hash, size, default, rating)
