# K-UP API

## This doc goes over all endpoints data provided end returned

Note: All endpoints but root endpoint accept POST requests due to jwt token based authentication


```
# endpoint
/ [GET]

# returns
{
    "status": 200,
    "app": "K-UP API"
}
```

Note: All endpoints from now on accept data 'wrapped' in jwt tokens. The actual wrapped data will be called **payload**

```
# endpoint
/new_user [POST]

# payload
{
    "email": str,
    "surname": str,
    "email": str,
    "password": str
}

# on OK
{
    "status": 201,
    "msg": "created"
}

```

```
# endpoint
/delete_user [POST]

# payload
{
    "id": int
}

# on OK
{
    "status": 200,
    "msg": "success"
}

```

```
# endpoint
/show_user/<id:int> [POST]

# payload {}

# on OK
{
    "status": 200,
    "msg": "success",
    "users": [user] # list contains one user
}

# user type
user = {
    "id": int,
    "name": str,
    "surname":  str,
    "email": str
}

```

```
# endpoint
/show_user [POST]

# payload {}

# on OK
{
    "status": 200,
    "msg": "success",
    "users": [user, user, user] # list contains zero or more users
}

# user type
user = {
    "id": int,
    "name": str,
    "surname":  str,
    "email": str
}

```
```
# endpoint
/login [POST]

# payload 
{
    "email": str,
    "password": str
}

# on OK
{
    "status": 200,
    "msg": "success",
    "id": int # list contains zero or more users
}
# on Err
{
    "status": 400,
    "msg": "incorrect login"
}
```

```
# endpoint
/tags [POST]

# payload {}

# on OK
{
    "status": 200,
    "tags": [tag, tag, tag, tag]
}

# tag type
tag = {
    "id": int,
    "name": str,
    "description": str
}
```


```
# endpoint
/new_post [POST]

# payload 
{
    "user_id": str,
    "type": str, # 'seek' or 'offer' 
    "title": str,
    "content": str,
    "tags": [] # List of ids of tags - might be null
}

# on OK
{
    "status": 201,
    "msg": "created",
    "id": int #id of newly created post
}

# TODO: add id of post as a response from API

# on Err
{
    "status": 400,
    "msg": "bad request"
}
```

```
# endpoint
/posts/<id:int> [POST]

# payload {}

# on OK
{
    "status": 200,
    "msg": "success",
    "users": [post] # list contains one user
}

# post type
post = {
    "id": str,
    "user_id": str,
    "type": str, # 'seek' or 'offer' 
    "title": str,
    "content": str,
    "tags": [] # List of ids of tags - might be null,
    "date": timestamp # seconds since epoch
}

```

```
# endpoint
/posts [POST]

# payload {}

# on OK
{
    "status": 200,
    "msg": "success",
    "users": [post, post] # list contains zero or more users
}

# post type
post = {
    "id": str,
    "user_id": str,
    "type": str, # 'seek' or 'offer' 
    "title": str,
    "content": str,
    "tags": [] # List of ids of tags - might be null,
    "date": timestamp # seconds since epoch
}

```

```
# endpoint
/delete_post [POST]

# payload {
    "id": int
}

# on OK
{
    "status": 200,
    "msg": "success",
}


```



### Error codes

#### Bad Request
```
{
    "status": 400,
    "msg": "bad request"
}
```

#### Unuthorized
```
{
    "status": 401,
    "msg": "user not authorized"
}
```

#### Internal Server Error
```
{
    "status": 503,
    "msg"
}
```
