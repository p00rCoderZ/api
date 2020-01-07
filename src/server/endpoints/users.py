from sanic.response import json
from asyncpg.exceptions import UniqueViolationError
from db import Db
from app import SERIAL
from .validate import validate_user, extract_jwt, validate_post, validate_deletion
from .response import Responses, create_response

import jwt
import asyncio

import jwt
import asyncio

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
                return json(create_response(Responses.OK))
            except UniqueViolationError as e:
                return json(create_response(Responses.BAD_REQUEST, {"msg": "user already exists"}))
    return json(create_response(Responses.UNAUTHORIZED))

async def delete_user(request):
    ok, payload = extract_jwt(request.body, SERIAL)
    if ok:
        q = "UPDATE users SET soft_delete='t' WHERE id={}"
        db_conn = Db.get_pool()
        try:
            await db_conn.fetchval(q.format(payload['id']))
            return json(create_response(Responses.OK))
        except:
            return json(create_response(Responses.BAD_REQUEST))
    return json(create_response(Responses.UNAUTHORIZED))

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
            return json(create_response(Responses.OK, {"users": [user]}))
        except:
            return json(create_response(Responses.BAD_REQUEST, {"users": []}))
    return json(create_response(Responses.UNAUTHORIZED))

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
            return json(create_response(Responses.OK, {"users": users}))
        except:
            return json(create_response(Responses.BAD_REQUEST, {"msg": "User does not exist", "users": []}))
    return json(create_response(Responses.UNAUTHORIZED))