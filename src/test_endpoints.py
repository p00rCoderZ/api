import unittest
import subprocess
import requests
import time
import pytest
import psycopg2
from urllib3.exceptions import NewConnectionError

API_PORT=8000
DSN = 'postgres://pros:foobar@postgres:5432/_test'


class EndpointTest(unittest.TestCase):
    def setUp(self):
        self._restart_test_db()
        self.sb = subprocess.Popen('/usr/api/src/server/server.py')
        self._wait_for_port()
        self.conn = psycopg2.connect(DSN)

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
        queries = ["DROP DATABASE IF EXISTS _test", "CREATE DATABASE _test" ]
        for q in queries:
            subprocess.call(['psql', '-c {}'.format(q)])
        
        subprocess.call(['psql', '-d_test', '-a', '-f/schema.sql'])

    def test_root(self):
        r = requests.get('http://localhost:8000/')
        payload = r.json()
        self.assertEqual(payload["status"], 200)
        self.assertEqual(payload["app"], "K-UP API")

    def test_db_clear_after_restart(self):
        cur = self.conn.cursor()
        q = "INSERT INTO users (name, surname, email, password) VALUES ('{name}', '{surname}', '{email}', '{password}') RETURNING *"
        user = {
            "name": 'test',
            "surname": "surname",
            "email": 'email',
            "password": 'passwd'
        }
        cur.execute(q.format(**user))

        cur.execute("SELECT id FROM users ORDER BY id DESC LIMIT 1")
        self.assertEqual(cur.fetchone()[0], 1)