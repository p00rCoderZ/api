import unittest
import subprocess
import requests
import time
import pytest
from urllib3.exceptions import NewConnectionError

API_PORT=8000

class EndpointTest(unittest.TestCase):
    def setUp(self):
        self.sb = subprocess.Popen('/usr/api/src/server/server.py')
        self._wait_for_port()

    def tearDown(self):
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

    def test_root(self):
        r = requests.get('http://localhost:8000/')
        payload = r.json()
        self.assertEqual(payload["status"], 200)
        self.assertEqual(payload["app"], "K-UP API")