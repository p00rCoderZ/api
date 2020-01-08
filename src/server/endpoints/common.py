from sanic.request import Request
from .response import create_response, Responses
from sanic.response import json, HTTPResponse
from app import SERIAL
import functools
from .validate import extract_jwt
import traceback

def jwt(f):
    async def wrapper(request: Request, *args, **kwargs) -> HTTPResponse:
        ok, payload = extract_jwt(request.body, SERIAL)
        if ok:
            try:
                return json(await f(payload, *args, **kwargs))
            except Exception as e:
                print(traceback.format_exc())
                return json(create_response(Responses.BAD_REQUEST))
        else:
            return json(create_response(Responses.UNAUTHORIZED))
    return wrapper

def no_jwt(f):
    async def wrapper(request: Request, *args, **kwargs) -> HTTPResponse:
        try:
            return json(await f(request.body, *args, **kwargs))
        except Exception as e:
            print(traceback.format_exc())
            return json(create_response(Responses.BAD_REQUEST))
    return wrapper