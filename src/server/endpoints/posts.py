from sanic.response import json
from asyncpg.exceptions import UniqueViolationError
from db import Db
from app import SERIAL
from .validate import validate_user, extract_jwt, validate_post, validate_deletion

import jwt
import asyncio

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
                    "status": row['status']
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

async def post(request, id):
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
                    "status": row['status']
                }
            q = """SELECT tag_id FROM post_tags WHERE post_id={}"""
            tags_rows = await conn.fetch(q.format(row['id']))
            tags = [tag['tag_id'] for tag in tags_rows]
            temp.update({"tags": tags})

            return json({"status": 200, "posts": [temp]})
        except:
            return json({"status": 400, "error_message": "Bad request", "posts": []})
    return json({"status": 400, "error_message": "Bad request", "posts": []})

async def delete_post(request):
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