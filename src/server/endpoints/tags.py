from sanic.response import json, HTTPResponse
from sanic.request import Request
from asyncpg.exceptions import UniqueViolationError
from db import Db
from app import SERIAL
from .validate import validate_user, extract_jwt, validate_post, validate_deletion
from .response import Responses, create_response
from .common import jwt

@jwt
async def tags(payload: dict) -> dict:
    conn = Db.get_pool()
    rows = await conn.fetch("""SELECT * FROM tags""")
    tags = [{"id": tag['id'], "name": tag['name'], "description": ['description']} for tag in rows]
    return create_response(Responses.OK, {"tags": tags})