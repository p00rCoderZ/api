import jwt
from jwt.exceptions import InvalidSignatureError, DecodeError
from db import Db

def validate_user(data):
    has_key_not_empty = lambda key: key in data and data[key]

    keys = ['name', 'surname', 'email', 'password']
    return all(has_key_not_empty(k) for k in keys)

def validate_post(data):
    return True

async def validate_deletion(data):
    has_key_not_empty = lambda key: key in data and data[key]

    keys = ['id', 'user_id']
    if not all(has_key_not_empty(k) for k in keys):
        print("keys")
        return False
    
    conn = Db.get_pool()
    q = """ SELECT user_id FROM posts WHERE id={} """.format(data['id'])
    post_author_id = await conn.fetch(q)
    post_author_id = post_author_id[0]['user_id']
    return post_author_id == data['user_id']

def extract_jwt(token, serial):
    try:
        payload = jwt.decode(token, serial, algorithm='HS256')
        return (True, payload)
    except (InvalidSignatureError, DecodeError):
        return (False, None)