import jwt
from jwt.exceptions import InvalidSignatureError, DecodeError
def validate_user(data):
    has_key_not_empty = lambda key: key in data and data[key]

    keys = ['name', 'surname', 'email', 'password']
    return all(has_key_not_empty(k) for k in keys)

def extract_jwt(token, serial):
    try:
        payload = jwt.decode(token, serial, algorithm='HS256')
        return (True, payload)
    except (InvalidSignatureError, DecodeError):
        return (False, None)