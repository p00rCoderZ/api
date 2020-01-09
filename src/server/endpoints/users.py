from asyncpg.exceptions import UniqueViolationError
from db import Db
from app import SERIAL
from .validate import check_keys_in_payload, validate_deletion
from .response import Responses, create_response
from .common import jwt

from passlib.apps import custom_app_context as pwd_context

@jwt
async def new_user(payload: dict) -> dict:
    keys = ['name', 'surname', 'email', 'password']
    if check_keys_in_payload(payload, keys):
        db_conn = Db.get_pool()
        hash = pwd_context.hash(payload["password"])
        payload.update({"password": hash})
        q = "INSERT INTO users (name, surname, email, password) VALUES ('{name}', '{surname}', '{email}', '{password}') RETURNING *"
        try:
            lets_see = await db_conn.fetchval(q.format(**payload))
            return create_response(Responses.CREATED)
        except UniqueViolationError as e:
            return create_response(Responses.BAD_REQUEST, {"msg": "user already exists"})
    else:
        return create_response(Responses.BAD_REQUEST, {"msg": "incorrect user data"})

@jwt
async def login(payload: dict) -> dict:
    if check_keys_in_payload(payload, ['email', 'password']):
        db_conn = Db.get_pool()
        q = "SELECT id, password FROM users WHERE email='{}'"
        row = await db_conn.fetch(q.format(payload["email"]))
        if row:
            row = row[0]
            id, hashed_passwd = row['id'], row['password']
            if pwd_context.verify(payload["password"], hashed_passwd):
                return create_response(Responses.OK, {"id": id})
                
        return create_response(Responses.BAD_REQUEST, {"msg": "incorrect login"})
    else:
        return create_response(Responses.BAD_REQUEST)

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