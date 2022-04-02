import math


async def parse_units(volume):
    if volume < 1024:
        return f'{volume} B'
    elif 1024 < volume < pow(1024, 2):
        return f'{round(volume / 1024, 2)} KiB'
    elif pow(1024, 2) < volume < pow(1024, 3):
        return f'{round(volume / pow(1024, 2), 2)} MiB'
    elif volume > pow(1024, 3):
        return f'{round(volume / pow(1024, 3), 2)} GiB'


async def shorten_line(line, length):
    if ' ' not in line or len(line.split(' ')[0] + '~') >= length:
        return line[:length - 1] + '~'
    result = ''
    for each in line.split(' '):
        between = result + ' ' + each
        if len(between.lstrip() + '~') > length:
            return result.lstrip() + '~'
        result = between


async def parse_title(title, length):
    if len(title) > length:
        return await shorten_line(title, length)
    return title


async def iter_pages(page, last_page):
    if last_page <= 15:
        return list(range(1, last_page + 1))
    if page <= 10:
        return [i for i in range(1, 12)] + [0] + \
               [i for i in range(last_page - 2, last_page + 1)]
    if page >= last_page - 9:
        return [i for i in range(1, 4)] + [0] + \
               [i for i in range(last_page - 10, last_page + 1)]
    return [i for i in range(1, 5)] + [0] + \
           [i for i in range(page - 2, page + 3)] + \
           [0] + [i for i in range(last_page - 3, last_page + 1)]


async def parse_page(request):
    page = request.query_params.get('page', '1')
    try:
        return int(page)
    except ValueError:
        return 0


async def parse_last_page(page, per_page, num):
    last = math.ceil(num / per_page) or 1
    if page == 0 or page > last:
        return 0
    return last
