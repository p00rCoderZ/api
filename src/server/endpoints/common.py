from sanic.request import Request
from .response import create_response, Responses
from sanic.response import json, HTTPResponse
from app import SERIAL
import functools
from .validate import extract_jwt

def jwt(f):
    async def wrapper(request: Request, *args, **kwargs) -> HTTPResponse:
        ok, payload = extract_jwt(request.body, SERIAL)
        if ok:
            return json(await f(payload, *args, **kwargs))
        else:
            return json(create_response(Responses.UNAUTHORIZED))
    return wrapper