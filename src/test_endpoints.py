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
class EndpointTest(unittest.TestCase):
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

    def test_root(self):
        r = requests.get('http://localhost:8000/')
        payload = r.json()
        self.assertEqual(payload["status"], 200)
        self.assertEqual(payload["app"], "K-UP API")

    def _wrap_payload(self, payload):
        return jwt.encode(payload, 'serial', algorithm='HS256')

    def _send_post_request(self, URL, payload, response_code=200, wrap_payload=True):
        r = requests.post(URL, data=self._wrap_payload(payload) if wrap_payload else payload)

        self.assertEqual(r.json()["status"], response_code)

        return r

    def _insert_new_user(self, user=None, response_code=200):
        user = DEFAULT_USER if user is None else user
        return self._send_post_request(API_URL + 'new_user', payload=user, response_code=response_code)

    def test_jwt(self):
        r = self._send_post_request(API_URL + 'jwt', payload={"test": "test"})
        self.assertEqual(r.json()["payload"], {"test": "test"})
        bad_token = jwt.encode({"test": "test"}, key="badkey", algorithm='HS256')
        r = self._send_post_request(API_URL + 'jwt', payload=bad_token, response_code=400, wrap_payload=False)
        self.assertEqual(r.json()["status"], 400)
        self.assertEqual(r.json()["error_message"], "User not authenticated")

    def test_db_clear_after_restart(self):
        q = "INSERT INTO users (name, surname, email, password) VALUES ('{name}', '{surname}', '{email}', '{password}') RETURNING *"
        user = DEFAULT_USER
        self.cur.execute(q.format(**user))

        self.cur.execute("SELECT id FROM users ORDER BY id DESC LIMIT 1")
        self.assertEqual(self.cur.fetchone()[0], 1)

    def test_new_user(self):
        self._insert_new_user()

        self.cur.execute("SELECT id FROM users ORDER BY id DESC LIMIT 1")
        self.assertEqual(self.cur.fetchone()[0], 1)

        second_user = DEFAULT_USER
        second_user.update({"email": "second_mail"})
        self._insert_new_user(second_user)
        self.cur.execute("SELECT count(*) FROM users")
        self.assertEqual(self.cur.fetchone()[0], 2)

    def test_same_user_twice(self):
        self._insert_new_user()
        r = self._insert_new_user(response_code=400)
        self.assertEqual(r.json()["error_message"], "User already exists")

    def test_soft_delete(self):
        self._insert_new_user()

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
        temp_user = DEFAULT_USER
        del temp_user['password']
        temp_user.update({"id": 1})
        self.assertEqual(r.json()["users"][0], DEFAULT_USER)

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
        first_user = DEFAULT_USER
        del first_user['password']
        first_user.update({"id": 1})
        self.assertEqual(r.json()["users"][0], DEFAULT_USER)

        r = self._send_post_request(API_URL + 'users/2', payload={})
        self.assertEqual(len(r.json()["users"]), 1)
        del second_user['password']
        self.assertEqual(r.json()["users"][0], second_user)

    def test_new_post(self):
        self._insert_new_user()
        post = {
            "type": "seek",
            "title": "Hello",
            "user_id": 1,
            "content": "Huge amount of content",
            'tags': [1, 2]
        }
        r = self._send_post_request(API_URL + 'new_post', payload=post)
        r = self._send_post_request(API_URL + 'posts', payload={})
        r = self._send_post_request(API_URL + 'posts/1', payload={})

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
            'tags': [1, 2]
        }
        r = self._send_post_request(API_URL + 'new_post', payload=post)
        r = self._send_post_request(API_URL + 'delete_post', payload={"id": 1, "user_id": 1})

    def test_tags(self):
        r = self._send_post_request(API_URL + 'tags', payload={})
        
        tags = r.json()['tags']
        self.assertEqual(len(tags), 2)

        keys = ["id", "name", "description"]
        self.assertEqual(
            all(key in d.keys() for key in keys for d in tags), True
        )

