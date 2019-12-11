#! /usr/local/bin/python3
from sanic import Sanic
from sanic.response import json
from asyncpg.exceptions import UniqueViolationError
from db import Db
from validate import validate_user

import jwt
import asyncio

app = Sanic()
DSN = 'postgres://pros:foobar@postgres:5432/kup'

@app.route("/jwt", methods=['POST'])
async def test(request):
    print(request.body)
    try:
        d = jwt.decode(request.body, 'serial', algorithm='HS256')
        return json({"status": 200, "msg": "Success"})
    except jwt.exceptions.InvalidSignatureError:
        return json({"status": 400, "msg": "User not authenticated"})

@app.route("/", methods=['GET'])
async def root(request):
    return json({"status": 200, "app": "K-UP API"})

@app.route("/new_user", methods=['POST'])
async def new_user(request):
    request = request.json
    if validate_user(request):
        print('Inserting new user to db')
        db_conn = Db.get_pool()
        q = "INSERT INTO users (name, surname, email, password) VALUES ('{name}', '{surname}', '{email}', '{password}') RETURNING *"
        try:
            lets_see = await db_conn.fetchval(q.format(**request))
            print(lets_see)
            return json({"status": 200, "id": lets_see})
        except UniqueViolationError as e:
            return json({"status": 400, "error_msg": "User already exists"})
    else:
        return json({"status:": 400, "error_msg": "Bad request"})

@app.route("/delete_user", methods=['POST'])
async def delete_user(request):
    request = request.json
    q = "UPDATE users SET soft_delete='t' WHERE id={}"
    db_conn = Db.get_pool()
    try:
        await db_conn.fetchval(q.format(request['id']))
        return json({"status": 200})
    except:
        return json({"status": 400})


async def main():
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