async def change_udata(rc, data, permissions):
    if await rc.exists(data):
        await rc.hset(data, key='permissions', value=','.join(permissions))
