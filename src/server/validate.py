def validate_user(data):
    has_key_not_empty = lambda key: key in data and data[key]

    keys = ['name', 'surname', 'email', 'password']
    return all(has_key_not_empty(k) for k in keys)