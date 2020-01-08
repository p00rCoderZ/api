from db import Db
from .response import Responses, create_response
from .common import jwt

@jwt
async def tags(payload: dict) -> dict:
    conn = Db.get_pool()
    rows = await conn.fetch("""SELECT * FROM tags""")
    tags = [{"id": tag['id'], "name": tag['name'], "description": ['description']} for tag in rows]
    return create_response(Responses.OK, {"tags": tags})