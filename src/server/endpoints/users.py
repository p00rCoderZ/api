from sanic.response import json
from asyncpg.exceptions import UniqueViolationError
from db import Db
from app import SERIAL
from .validate import validate_user, extract_jwt, validate_post, validate_deletion

import jwt
import asyncio

import jwt
import asyncio

# @app.route("/new_user", methods=['POST'])
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

# @app.route("/delete_user", methods=['POST'])
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

# @app.route("/users/<id:int>", methods=['POST'])
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

# @app.route("/users", methods=['POST'])
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