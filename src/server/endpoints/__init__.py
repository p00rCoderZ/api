#! /usr/local/bin/python3

from sanic.response import json
from asyncpg.exceptions import UniqueViolationError
from db import Db
from app import SERIAL
from .validate import validate_user, extract_jwt, validate_post, validate_deletion

import jwt
import asyncio

from .users import new_user, delete_user, show_user, show_users
from .posts import new_post, post, posts, delete_post
from .tags import tags
from .common import jwt, no_jwt
from .response import create_response, Responses

@jwt
async def test(payload: dict) -> dict:
    return create_response(Responses.OK, {"payload": payload})

@no_jwt
async def root(payload: dict) -> dict:
    return create_response(Responses.OK, {"app": "K-UP API"})

def init(app):
    app.add_route(root, '/', methods=['GET'])
    app.add_route(test, '/jwt', methods=['POST'])
    app.add_route(new_user, '/new_user', methods=['POST'])
    app.add_route(delete_user, "/delete_user", methods=['POST'])
    app.add_route(show_user, "/users/<id:int>", methods=['POST'])
    app.add_route(show_users, "/users", methods=['POST'])
    app.add_route(new_post, "/new_post", methods=['POST'])
    app.add_route(delete_post, "/delete_post", methods=['POST'])
    app.add_route(post, "/posts/<id:int>", methods=['POST'])
    app.add_route(posts, "/posts", methods=['POST'])
    app.add_route(tags, "/tags", methods=['POST'])