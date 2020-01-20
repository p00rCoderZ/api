from db import Db
from app import SERIAL
from .validate import validate_post, validate_deletion
from .response import Responses, create_response
from .common import jwt
from datetime import datetime

def post_from_db(row):
    return {
        "id": row['id'],
        "type": row['type'],
        "title": row['title'],
        "user_id": row['user_id'],
        "content": row['content'],
        "status": row['status'],
        "date": row["datetime"]
    }

from asyncpg.exceptions import ForeignKeyViolationError
@jwt
async def new_post(payload: dict) -> dict:
    if validate_post(payload):
        db_conn = Db.get_pool()
        async with db_conn.acquire() as conn:
            async with conn.transaction():
                q = """INSERT INTO posts (user_id, type, title, content) VALUES
                    ($1, $2, $3, $4) RETURNING *
                """
                new_post_id = await conn.fetchval(q, payload["user_id"], payload["type"],
                    payload["title"], payload["content"]
                )
                q = """INSERT INTO post_tags (post_id, tag_id) values ($1, $2) RETURNING *
                """
                if 'tags' in payload:
                    for tag in payload['tags']:
                        try:
                            await conn.fetchval(q, new_post_id, tag)
                        except ForeignKeyViolationError as e:
                            return create_response(Responses.BAD_REQUEST)
        return create_response(Responses.CREATED, {"id": new_post_id})
    else:
        return create_response(Responses.BAD_REQUEST)

@jwt
async def posts(payload: dict) -> dict:
    conn = Db.get_pool()
    rows = await conn.fetch("""SELECT * FROM posts""")
    posts = []
    for row in rows:
        temp = post_from_db(row)
        q = """SELECT tag_id FROM post_tags WHERE post_id=$1"""
        tags_rows = await conn.fetch(q, row['id'])
        tags = [tag['tag_id'] for tag in tags_rows]
        temp.update({"tags": tags})
        posts.append(temp)
    return create_response(Responses.OK, {"posts": posts})

@jwt
async def post(payload: dict, id: int) -> dict:
    conn = Db.get_pool()
    row = await conn.fetch("""SELECT * FROM posts WHERE id=$1""", id)
    row = row[0]
    temp = post_from_db(row)
    q = """SELECT tag_id FROM post_tags WHERE post_id=$1"""
    tags_rows = await conn.fetch(q, row['id'])
    tags = [tag['tag_id'] for tag in tags_rows]
    temp.update({"tags": tags})

    return create_response(Responses.OK, {"posts": [temp]})

@jwt
async def delete_post(payload: dict) -> dict:
    if await validate_deletion(payload):
        conn = Db.get_pool()
        row = await conn.fetch("""UPDATE posts SET status='inactive' WHERE id=$1""", payload['id'])
        return create_response(Responses.OK)
    else:
        return create_response(Responses.BAD_REQUEST)