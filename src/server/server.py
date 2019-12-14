#! /usr/local/bin/python3
from sanic import Sanic
from sanic.response import json
from asyncpg.exceptions import UniqueViolationError
from db import Db
from validate import validate_user, extract_jwt, validate_post, validate_deletion

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

@app.route("/users/<id:int>", methods=['POST'])
async def show_user(request, id):
    ok, _ = extract_jwt(request.body, SERIAL)
    if ok:
        q = "SELECT * FROM users WHERE id={}"
        db_conn = Db.get_pool()
        try:
            user = await db_conn.fetch(q.format(id))
            user = user[0]
            user = {
                "id": user["id"],
                "name": user["name"],
                "surname": user["surname"],
                "email": user["email"]
            }
            return json({"status": 200, "users": [user]})
        except:
            raise
            # return json({"status": 400, "error_message": "User does not exist", "users": []})
    return json({"status:": 400, "error_message": "Bad request", "users": []})

@app.route("/users", methods=['POST'])
async def show_users(request):
    ok, _ = extract_jwt(request.body, SERIAL)
    if ok:
        q = "SELECT * FROM users"
        db_conn = Db.get_pool()
        users = []
        try:
            rows = await db_conn.fetch(q)
            for user in rows:
                users.append({
                    "id": user["id"],
                    "name": user["name"],
                    "surname": user["surname"],
                    "email": user["email"]
                })
            return json({"status": 200, "users": users})
        except:
            return json({"status": 400, "error_message": "User does not exist", "users": []})
    return json({"status:": 400, "error_message": "Bad request", "users": []})

@app.route("/new_post", methods=['POST'])
async def new_post(request):
    ok, payload = extract_jwt(request.body, SERIAL)
    if ok and validate_post(payload):
        db_conn = Db.get_pool()
        try:
            async with db_conn.acquire() as conn:
                async with conn.transaction():
                    q = """INSERT INTO posts (user_id, type, title, content) VALUES
                        ({user_id}, '{type}', '{title}', '{content}') RETURNING id
                    """
                    print(q.format(**payload))
                    new_post_id = await conn.fetchval(q.format(**payload))
                    print(new_post_id)
                    q = """INSERT INTO post_tags (post_id, tag_id) values ({}, {}) RETURNING *
                    """
                    for tag in payload['tags']:
                        print('Inserting tags {}'.format(q.format(new_post_id, tag)))
                        await conn.fetchval(q.format(new_post_id, tag))
        except:
            return json({"status": 400, "error_message": "Bad request"})
        else:
            return json({"status": 200})
    return json({"status": 400, "error_message": "Bad request"})

@app.route("/posts", methods=['POST'])
async def posts(request):
    ok, _ = extract_jwt(request.body, SERIAL)
    if ok:
        db_conn = Db.get_pool()
        try:
            conn = Db.get_pool()
            rows = await conn.fetch("""SELECT * FROM posts""")
            posts = []
            for row in rows:
                temp = {
                    "id": row['id'],
                    "type": row['type'],
                    "title": row['title'],
                    "user_id": row['user_id'],
                    "content": row['content'],
                }
                q = """SELECT tag_id FROM post_tags WHERE post_id={}"""
                tags_rows = await conn.fetch(q.format(row['id']))
                tags = [tag['tag_id'] for tag in tags_rows]
                temp.update({"tags": tags})
                posts.append(temp)
            return json({"status": 200, "posts": posts})
        except:
            return json({"status": 400, "error_message": "Bad request"})
    return json({"status": 400, "error_message": "Bad request"})

@app.route("/posts/<id:int>", methods=['POST'])
async def posts(request, id):
    ok, _ = extract_jwt(request.body, SERIAL)
    if ok:
        db_conn = Db.get_pool()
        try:
            conn = Db.get_pool()
            row = await conn.fetch("""SELECT * FROM posts WHERE id={}""".format(id))
            row = row[0]
            temp = {
                    "id": row['id'],
                    "type": row['type'],
                    "title": row['title'],
                    "user_id": row['user_id'],
                    "content": row['content'],
                }
            q = """SELECT tag_id FROM post_tags WHERE post_id={}"""
            tags_rows = await conn.fetch(q.format(row['id']))
            tags = [tag['tag_id'] for tag in tags_rows]
            temp.update({"tags": tags})

            return json({"status": 200, "posts": [temp]})
        except:
            return json({"status": 400, "error_message": "Bad request", "posts": []})
    return json({"status": 400, "error_message": "Bad request", "posts": []})

@app.route("/delete_post", methods=['POST'])
async def posts(request):
    ok, payload = extract_jwt(request.body, SERIAL)
    if ok and await validate_deletion(payload):
        db_conn = Db.get_pool()
        try:
            conn = Db.get_pool()
            row = await conn.fetch("""UPDATE posts SET status='inactive' WHERE id={}""".format(payload['id']))
            return json({"status": 200})
        except:
            return json({"status": 400, "error_message": "Bad request"})
    return json({"status": 400, "error_message": "Bad request"})

@app.route("/tags", methods=['POST'])
async def tags(request):
    ok, _ = extract_jwt(request.body, SERIAL)
    if ok:
        try:
            conn = Db.get_pool()
            rows = await conn.fetch("""SELECT * FROM tags""")
            tags = [{"id": tag['id'], "name": tag['name'], "description": ['description']} for tag in rows]
            return json({"status": 200, "tags": tags})
        except:
            return json({"status": 400, "error_message": "Bad request", "tags": []})
    return json({"status": 400, "error_message": "Bad request", "tags": []})

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