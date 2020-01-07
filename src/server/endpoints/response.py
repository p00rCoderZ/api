from enum import Enum
from collections import namedtuple
from typing import Dict

class Responses(Enum):
    OK = {
        "status": 200,
        "msg": "sucess"
    }

    BAD_REQUEST = {
        "status": 400,
        "msg": "bad request"
    }

    UNAUTHORIZED = {
        "status": 401,
        "msg": "user not authorized"
    }

def create_response(resp: Responses, add: dict={}) -> Dict:
    new_resp = resp.value
    new_resp.update(add)
    return new_resp