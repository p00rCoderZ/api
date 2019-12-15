#! /usr/local/bin/python3
from asyncpg.exceptions import UniqueViolationError
from db import Db

import jwt
import asyncio
import toml

from app import app, DSN

import endpoints

async def main():
    endpoints.init(app)
    await Db.init(DSN)
    db_conn = Db.get_pool()

    works = await db_conn.fetch('SELECT * from tags')
    for w in works:
        print('id: {}, desc: {}, name: {}'.format(w['id'], w['description'], w['name']))
    
    server = app.create_server(host="0.0.0.0", port=8000, return_asyncio_server=True)
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(server, loop=loop)

    return task        
if __name__ == "__main__":
    server = asyncio.ensure_future(main())
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt as e:
        asyncio.get_event_loop().stop()