from sanic.response import json
from asyncpg.exceptions import UniqueViolationError
from db import Db
from app import SERIAL
from .validate import validate_user, extract_jwt, validate_post, validate_deletion

import jwt
import asyncio

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