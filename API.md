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