from enum import Enum

class Responses(Enum):
    OK = {
        "status": 200,
        "msg": "success"
    }

    BAD_REQUEST = {
        "status": 400,
        "msg": "bad request"
    }

    UNAUTHORIZED = {
        "status": 401,
        "msg": "user not authorized"
    }

    CREATED = {
        "status": 201,
        "msg": "created"
    }

    INTERNAL = {
        "status": 500,
        "msg": "internal server error"
    }

def create_response(resp: Responses, add: dict={}) -> dict:
    new_resp = resp.value
    new_resp.update(add)
    return new_resp