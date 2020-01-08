from asyncpg.exceptions import UniqueViolationError
from db import Db
from app import SERIAL
from .validate import validate_user, validate_post, validate_deletion
from .response import Responses, create_response
from .common import jwt

@jwt
async def new_user(payload: dict) -> dict:
    db_conn = Db.get_pool()
    q = "INSERT INTO users (name, surname, email, password) VALUES ('{name}', '{surname}', '{email}', '{password}') RETURNING *"
    try:
        lets_see = await db_conn.fetchval(q.format(**payload))
        return create_response(Responses.CREATED)
    except UniqueViolationError as e:
        return create_response(Responses.BAD_REQUEST, {"msg": "user already exists"})

@jwt
async def delete_user(payload: dict) -> dict:
    q = "UPDATE users SET soft_delete='t' WHERE id={}"
    db_conn = Db.get_pool()
    await db_conn.fetchval(q.format(payload['id']))
    return create_response(Responses.OK)

@jwt
async def show_user(payload: dict, id: int) -> dict:
    q = "SELECT * FROM users WHERE id={}"
    db_conn = Db.get_pool()
    user = await db_conn.fetch(q.format(id))
    user = user[0]
    user = {
        "id": user["id"],
        "name": user["name"],
        "surname": user["surname"],
        "email": user["email"]
    }
    return create_response(Responses.OK, {"users": [user]})

@jwt
async def show_users(request: dict) -> dict:
    q = "SELECT * FROM users"
    db_conn = Db.get_pool()
    users = []
    rows = await db_conn.fetch(q)
    for user in rows:
        users.append({
            "id": user["id"],
            "name": user["name"],
            "surname": user["surname"],
            "email": user["email"]
        })
    return create_response(Responses.OK, {"users": users})