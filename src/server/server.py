#! /usr/local/bin/python3
from sanic import Sanic
from sanic.response import json
from asyncpg.exceptions import UniqueViolationError
from db import Db
from validate import validate_user, extract_jwt

import jwt
import asyncio
import toml

app = Sanic()
DBNAME = app.config['DBNAME'] if "DBNAME" in app.config else 'kup'
SERIAL = 'serial' if "DBNAME" in app.config else toml.load('/secrets.toml')['serial']
DSN = 'postgres://pros:foobar@postgres:5432/{}'.format(DBNAME)
 
@app.route("/jwt", methods=['POST'])
async def test(request):
    payload = request.body
    ok, payload = extract_jwt(payload, SERIAL)
    if ok:
        return json({"status": 200, "payload": payload})
    else:
        return json({"status": 400, "error_message": "User not authenticated"})

@app.route("/", methods=['GET'])
async def root(request):
    return json({"status": 200, "app": "K-UP API"})

@app.route("/new_user", methods=['POST'])
async def new_user(request):
    ok, payload = extract_jwt(request.body, SERIAL)
    if ok:
        if validate_user(payload):
            print('Inserting new user to db')
            db_conn = Db.get_pool()
            q = "INSERT INTO users (name, surname, email, password) VALUES ('{name}', '{surname}', '{email}', '{password}') RETURNING *"
            try:
                lets_see = await db_conn.fetchval(q.format(**payload))
                print(lets_see)
                return json({"status": 200, "id": lets_see})
            except UniqueViolationError as e:
                return json({"status": 400, "error_message": "User already exists"})
    return json({"status:": 400, "error_message": "Bad request"})

@app.route("/delete_user", methods=['POST'])
async def delete_user(request):
    ok, payload = extract_jwt(request.body, SERIAL)
    if ok:
        q = "UPDATE users SET soft_delete='t' WHERE id={}"
        db_conn = Db.get_pool()
        try:
            await db_conn.fetchval(q.format(payload['id']))
            return json({"status": 200})
        except:
            return json({"status": 400, "error_message": "User does not exist"})
    return json({"status:": 400, "error_message": "Bad request"})

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