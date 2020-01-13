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
