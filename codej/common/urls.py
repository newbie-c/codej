import asyncio
import functools


def query_url(request, endpoint, **kwargs):
    path, query = dict(), dict()
    for key in kwargs:
        if key.endswith('_'):
            query[key] = kwargs[key]
        else:
            path[key] = kwargs[key]
    if query:
        params = [key.rstrip('_')+'='+str(query[key]) for key in query]
        params = '?' + '&'.join(params)
        return request.url_for(endpoint, **path) + params
    return request.url_for(endpoint, **path)


async def get_next(request, this_path):
    loop = asyncio.get_running_loop()
    url = await loop.run_in_executor(
        None, functools.partial(
            query_url, request, 'auth:login', next_=this_path))
    return url
