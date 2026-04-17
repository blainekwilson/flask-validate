"""
Smoke / repetition test using ``minimal_app`` (alphabetic ``name`` field).

``test_post`` sends many identical POSTs to ensure the decorator and
``SAFE_ALPHA`` rules stay stable under load (not a benchmark; loop count is
modest for CI speed).
"""
import unittest
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
sys.path.insert(0, os.path.abspath(os.path.join(_here, '..', 'src')))
from minimal_app import app


class AppTestCase(unittest.TestCase):
    """Uses the fixture app defined in ``minimal_app.py``."""

    def setUp(self):
        """Push app context and create a test client."""
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()


    def tearDown(self):
        """Pop the application context."""
        self.ctx.pop()

    def test_post(self):
        """Repeated POST with valid ``name``; expects 200 and echoed HTML body each time."""
        for _ in range(100):
            response = self.client.post("/", data={"name": "blaine"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_data(as_text=True), '<html><body>Name: blaine</body></html>')


if __name__ == "__main__":
    unittest.main()