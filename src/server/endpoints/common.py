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
                return await f(payload, *args, **kwargs)
            except Exception as e:
                return create_response(Responses.INTERNAL, {"traceback": traceback.format_exc()})
        else:
            return create_response(Responses.UNAUTHORIZED)
    return wrapper

def no_jwt(f):
    async def wrapper(request: Request, *args, **kwargs) -> HTTPResponse:
        try:
            return await f(request.body, *args, **kwargs)
        except Exception as e:
            return create_response(Responses.INTERNAL, {"traceback": traceback.format_exc()})
    return wrapper