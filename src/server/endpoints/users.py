from asyncpg.exceptions import UniqueViolationError
from db import Db
from app import SERIAL
from .validate import check_keys_in_payload, validate_deletion
from .response import Responses, create_response
from .common import jwt

from passlib.apps import custom_app_context as pwd_context

@jwt
async def new_user(payload: dict) -> dict:
    keys = ['nick', 'email', 'password']
    if check_keys_in_payload(payload, keys):
        db_conn = Db.get_pool()
        hashed = pwd_context.hash(payload["password"])
        q = "INSERT INTO users (nick, email, password) VALUES ($1, $2, $3) RETURNING *"
        try:
            lets_see = await db_conn.fetchval(q, payload['nick'], payload['email'], hashed)
            return create_response(Responses.CREATED)
        except UniqueViolationError as e:
            return create_response(Responses.BAD_REQUEST, {"msg": "user already exists"})
    else:
        return create_response(Responses.BAD_REQUEST, {"msg": "incorrect user data"})

@jwt
async def login(payload: dict) -> dict:
    if check_keys_in_payload(payload, ['email', 'password']):
        db_conn = Db.get_pool()
        q = "SELECT id, password FROM users WHERE email=$1"
        row = await db_conn.fetch(q, payload["email"])
        if row:
            row = row[0]
            id, hashed_passwd = row['id'], row['password']
            if pwd_context.verify(payload["password"], hashed_passwd):
                return create_response(Responses.OK, {"id": id})

        return create_response(Responses.BAD_REQUEST, {"msg": "incorrect login"})
    else:
        return create_response(Responses.BAD_REQUEST)

@jwt
async def nick_exists(payload: dict) -> dict:
    if check_keys_in_payload(payload, ['nick']):
        db_conn = Db.get_pool()
        q = "SELECT count(*) FROM users WHERE nick=$1"
        row = await db_conn.fetch(q, payload['nick'])
        if row:
            count = row[0][0]
            return create_response(Responses.OK, {"exists": count >= 1})

@jwt
async def email_exists(payload: dict) -> dict:
    if check_keys_in_payload(payload, ['email']):
        db_conn = Db.get_pool()
        q = "SELECT count(*) FROM users WHERE email=$1"
        row = await db_conn.fetch(q, payload['email'])
        if row:
            count = row[0][0]
            return create_response(Responses.OK, {"exists": count >= 1})

@jwt
async def delete_user(payload: dict) -> dict:
    q = "UPDATE users SET soft_delete='t' WHERE id=$1"
    db_conn = Db.get_pool()
    await db_conn.fetchval(q, payload['id'])
    return create_response(Responses.OK)

@jwt
async def show_user(payload: dict, id: int) -> dict:
    q = "SELECT * FROM users WHERE id=$1"
    db_conn = Db.get_pool()
    user = await db_conn.fetch(q, id)
    if user:
        user = user[0]
        user = {
            "id": user["id"],
            "nick": user["nick"],
            "name": user["name"],
            "surname": user["surname"],
            "email": user["email"]
        }
        return create_response(Responses.OK, {"users": [user]})
    return create_response(Responses.BAD_REQUEST)
    
@jwt
async def show_users(request: dict) -> dict:
    q = "SELECT * FROM users"
    db_conn = Db.get_pool()
    users = []
    rows = await db_conn.fetch(q)
    for user in rows:
        users.append({
            "id": user["id"],
            "nick": user["nick"],
            "name": user["name"],
            "surname": user["surname"],
            "email": user["email"]
        })
    return create_response(Responses.OK, {"users": users})