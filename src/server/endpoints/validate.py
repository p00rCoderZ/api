import jwt
from jwt.exceptions import InvalidSignatureError, DecodeError
from db import Db

from typing import List, Tuple, Mapping, Union

def check_keys_in_payload(payload: dict, keys: List[str]) -> bool:
    has_key_not_empty = lambda key: key in payload and payload[key]

    return all(has_key_not_empty(k) for k in keys)

def validate_post(payload: dict) -> bool:
    return True

async def validate_deletion(payload: dict) -> bool:
    keys = ['id', 'user_id']
    check_keys_in_payload(payload, keys)
    
    conn = Db.get_pool()
    q = """ SELECT user_id FROM posts WHERE id={} """.format(data['id'])
    post_author_id = await conn.fetch(q)
    post_author_id = post_author_id[0]['user_id']
    return post_author_id == data['user_id']

def extract_jwt(token: Union[str, bytes], serial: Union[str, bytes]) -> Tuple[bool, dict]:
    try:
        payload = jwt.decode(token, serial, algorithm='HS256')
        return (True, payload)
    except (InvalidSignatureError, DecodeError):
        return (False, None)