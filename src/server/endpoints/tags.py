from sanic.response import json
from asyncpg.exceptions import UniqueViolationError
from db import Db
from app import SERIAL
from .validate import validate_user, extract_jwt, validate_post, validate_deletion
from .response import Responses, create_response

import jwt
import asyncio

async def tags(request):
    ok, _ = extract_jwt(request.body, SERIAL)
    if ok:
        try:
            conn = Db.get_pool()
            rows = await conn.fetch("""SELECT * FROM tags""")
            tags = [{"id": tag['id'], "name": tag['name'], "description": ['description']} for tag in rows]
            return json(create_response(Responses.OK, {"tags": tags}))
        except:
            return json(create_response(Responses.BAD_REQUEST))
    return json(create_response(Responses.UNAUTHORIZED))