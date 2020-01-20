from enum import Enum
from sanic import response
import copy
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

def create_response(resp: Responses, add: dict={}) -> response.HTTPResponse:
    new_resp = copy.deepcopy(resp.value)
    print(new_resp)
    status = copy.deepcopy(new_resp["status"])
    del new_resp["status"]
    new_resp.update(add)
    print("status: {}".format(status))
    return response.json(body=new_resp, status=status)