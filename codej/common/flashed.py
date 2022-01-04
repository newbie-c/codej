async def get_flashed(request):
    if current := request.session.get('flashed'):
        res = [message for message in current]
        del request.session['flashed']
        return res


async def set_flashed(request, message):
    if request.session.get('flashed', None) is None:
        request.session['flashed'] = [message]
    else:
        request.session['flashed'].append(message)
