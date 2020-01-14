import unittest
import subprocess
import requests
import time
import pytest
import psycopg2
import os
import json
import jwt
from urllib3.exceptions import NewConnectionError
from copy import deepcopy
API_PORT=8000
API_URL = 'http://localhost:8000/'
DSN = 'postgres://pros:foobar@postgres:5432/_test'
DEFAULT_USER = {
    "name": 'test',
    "surname": "surname",
    "email": 'email',
    "password": 'passwd'
}
class EndpointBase(unittest.TestCase):
    def setUp(self):
        self._restart_test_db()
        self.sb = subprocess.Popen('/usr/api/src/server/server.py')
        self._wait_for_port()
        self.conn = psycopg2.connect(DSN)
        self.cur = self.conn.cursor()

    def tearDown(self):
        self.conn.close()
        self.sb.kill()

    def _wait_for_port(self, timeout=5, port=API_PORT):
        tout = time.monotonic() + timeout

        while time.monotonic() < tout:
            try:
                requests.get('http://localhost:{}/'.format(port))
            except Exception:
                time.sleep(0.1)
            else:
                return
        pytest.fail()

    def _restart_test_db(self):
        os.environ["SANIC_DBNAME"] = "_test"
        queries = ["DROP DATABASE IF EXISTS _test", "CREATE DATABASE _test" ]
        for q in queries:
            subprocess.call(['psql', '-c {}'.format(q)], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        
        subprocess.call(['psql', '-d_test', '-a', '-f/schema.sql'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    def _wrap_payload(self, payload):
        return jwt.encode(payload, 'serial', algorithm='HS256')

    def _send_post_request(self, URL, payload, response_code=200, wrap_payload=True):
        r = requests.post(URL, data=self._wrap_payload(payload) if wrap_payload else payload)
        
        print(r.json())
        self.assertIsNotNone(r.json())
        self.assertEqual(r.json()["status"], response_code)

        return r

    def _insert_new_user(self, user=None, response_code=201):
        user = DEFAULT_USER if user is None else user
        return self._send_post_request(API_URL + 'new_user', payload=user, response_code=response_code)

    def _perform_login(self, password='def_pas', email='def_mail', response_code=200):
        r = self._send_post_request(API_URL + 'login', payload={"email": email, "password": password}, response_code=response_code)
        if response_code == 200:
            self.assertTrue("id" in r.json())
        return r

class EndpointTest(EndpointBase):
    def test_root(self):
        r = requests.get('http://localhost:8000/')
        payload = r.json()
        self.assertEqual(payload["status"], 200)
        self.assertEqual(payload["app"], "K-UP API")

    def test_jwt(self):
        r = self._send_post_request(API_URL + 'jwt', payload={"test": "test"})
        self.assertEqual(r.json()["payload"], {"test": "test"})
        bad_token = jwt.encode({"test": "test"}, key="badkey", algorithm='HS256')
        r = self._send_post_request(API_URL + 'jwt', payload=bad_token, response_code=401, wrap_payload=False)
        self.assertEqual(r.json()["status"], 401)
        self.assertEqual(r.json()["msg"], "user not authorized")

    def test_db_clear_after_restart(self):
        q = "INSERT INTO users (name, surname, email, password) VALUES ('{name}', '{surname}', '{email}', '{password}') RETURNING *"
        user = DEFAULT_USER
        self.cur.execute(q.format(**user))

        self.cur.execute("SELECT id FROM users ORDER BY id DESC LIMIT 1")
        self.assertEqual(self.cur.fetchone()[0], 1)

class UserEndpointTest(EndpointBase):
    def test_new_user(self):
        self._insert_new_user()

        self.cur.execute("SELECT id FROM users ORDER BY id DESC LIMIT 1")
        self.assertEqual(self.cur.fetchone()[0], 1)

        second_user = deepcopy(DEFAULT_USER)
        second_user.update({"email": "second_mail"})
        self._insert_new_user(second_user)
        self.cur.execute("SELECT count(*) FROM users")
        self.assertEqual(self.cur.fetchone()[0], 2)

    def test_same_user_twice(self):
        self._insert_new_user()
        r = self._insert_new_user(response_code=400)
        self.assertEqual(r.json()["msg"], "user already exists")

    def test_soft_delete(self):
        self._insert_new_user()

        r = self._send_post_request(API_URL + 'delete_user', payload={"id": 1})
        self.assertEqual(r.json()["status"], 200)

        self.cur.execute("SELECT soft_delete FROM users WHERE id=1")
        self.assertEqual(self.cur.fetchone()[0], True)
    
    def test_soft_delete_twice(self):
        self._insert_new_user()

        r = self._send_post_request(API_URL + 'delete_user', payload={"id": 1})
        self.assertEqual(r.json()["status"], 200)

        r = self._send_post_request(API_URL + 'delete_user', payload={"id": 1})
        self.assertEqual(r.json()["status"], 200)

        self.cur.execute("SELECT soft_delete FROM users WHERE id=1")
        self.assertEqual(self.cur.fetchone()[0], True)

    def test_users(self):
        r = self._send_post_request(API_URL + 'users', payload={})
        self.assertEqual(r.json()["status"], 200)
        self.assertEqual(r.json()["users"], [])
        
        self._insert_new_user()
        r = self._send_post_request(API_URL + 'users', payload={})
        self.assertEqual(r.json()["status"], 200)
        self.assertEqual(len(r.json()["users"]), 1)
        temp_user = deepcopy(DEFAULT_USER)
        del temp_user['password']
        temp_user.update({"id": 1})
        self._perform_login(password=DEFAULT_USER["password"], email=DEFAULT_USER["email"])

    def test_user_not_existing(self):
        r = self._send_post_request(API_URL + 'users/1', payload={}, response_code=400)


    def test_specific_users(self):
        r = self._send_post_request(API_URL + 'users', payload={})
        self.assertEqual(r.json()["status"], 200)
        self.assertEqual(r.json()["users"], [])

        self._insert_new_user()

        second_user = deepcopy(DEFAULT_USER)
        second_user.update({"email": "second_email", "id": 2})
        self._insert_new_user(second_user)

        r = self._send_post_request(API_URL + 'users/1', payload={})
        self.assertEqual(len(r.json()["users"]), 1)
        first_user = deepcopy(DEFAULT_USER)
        del first_user['password']
        first_user.update({"id": 1})
        self.assertEqual(r.json()["users"][0], first_user)

        r = self._send_post_request(API_URL + 'users/2', payload={})
        self.assertEqual(len(r.json()["users"]), 1)
        del second_user['password']
        self.assertEqual(r.json()["users"][0], second_user)

    def test_login(self):
        self._insert_new_user()
        passwd, email = DEFAULT_USER['password'], DEFAULT_USER['email']
        self._perform_login(password=passwd, email=email)

    def test_incorrect_login(self):
        r = self._perform_login(response_code=400)
        self.assertEqual(r.json()['msg'], 'incorrect login')
    
    def test_incorrect_login_password(self):
        self._insert_new_user()

        r = self._perform_login(password=DEFAULT_USER["password"], response_code=400)
        self.assertEqual(r.json()['msg'], 'incorrect login')

    def test_incorrect_login_email(self):
        self._insert_new_user()

        r = self._perform_login(password=DEFAULT_USER["email"], response_code=400)
        self.assertEqual(r.json()['msg'], 'incorrect login')

    def test_invalid_data_login(self):
        r = requests.post(API_URL + 'login', data=self._wrap_payload({"id": 1}))
        self.assertEqual(r.json()["status"], 400)

        r = requests.post(API_URL + 'login', data=self._wrap_payload({"id": "pls break"}))
        self.assertEqual(r.json()["status"], 400)
        
        r = requests.post(API_URL + 'login', data=self._wrap_payload({"email": "'get rekt'"}))
        self.assertEqual(r.json()["status"], 400)

        r = requests.post(API_URL + 'login', data=self._wrap_payload({"password": "42",  "email": "'get rekt'"}))
        self.assertEqual(r.json()["status"], 400)
        
        r = requests.post(API_URL + 'login', data=self._wrap_payload({"password": 42,  "email": "'get rekt'"}))
        self.assertEqual(r.json()["status"], 400)
class PostsEndpointTest(EndpointBase):
    def test_new_post(self):
        self._insert_new_user()
        post = {
            "type": "seek",
            "title": "Hello",
            "user_id": 1,
            "content": "Huge amount of content",
            'tags': [1, 2]
        }
        r = self._send_post_request(API_URL + 'new_post', payload=post, response_code=201)
        r = self._send_post_request(API_URL + 'posts', payload={})
        post = r.json()['posts'][0]
        to_compare = {
            "id": 1,
            "type": "seek",
            "title": "Hello",
            "user_id": 1,
            "content": "Huge amount of content",
            'tags': [1, 2],
            'status': 'active'
        }
        self.assertEqual(post, to_compare)
        r = self._send_post_request(API_URL + 'posts/1', payload={})
        post = r.json()['posts'][0]
        self.assertEqual(post, to_compare)

    def test_new_post_invalid_data(self):
        self._insert_new_user()
        post = {
            "type": "seek",
            "title": "Hello",
            "user_id": 1,
            "content": "Huge amount of content",
            'tags': [1, 2, 3]
        }
        self._send_post_request(API_URL + 'new_post', payload=post, response_code=400)

    def test_delete_post(self):
        self._insert_new_user()
        post = {
            "type": "seek",
            "title": "Hello",
            "user_id": 1,
            "content": "Huge amount of content",
            'tags': [1, 2],
        }
        r = self._send_post_request(API_URL + 'new_post', payload=post, response_code=201)
        r = self._send_post_request(API_URL + 'delete_post', payload={"id": 1, "user_id": 1})

class TagEndpointTest(EndpointBase):
    def test_tags(self):
        r = self._send_post_request(API_URL + 'tags', payload={})
        
        tags = r.json()['tags']
        self.assertEqual(len(tags), 2)

        keys = ["id", "name", "description"]
        self.assertEqual(
            all(key in d.keys() for key in keys for d in tags), True
        )
