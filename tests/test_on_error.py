"""
Tests for custom `on_error` handler integration with the validation decorator.

Verifies that when validation fails and a custom `on_error` is supplied, the
handler is called and its Flask response is returned instead of the default
HTML error page.
"""
import unittest
import os
import sys
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)
sys.path.insert(0, os.path.abspath(os.path.join(_here, '..')))
sys.path.insert(0, os.path.abspath(os.path.join(_here, '..', 'src')))
from sample_app import app


class OnErrorTestCase(unittest.TestCase):
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()

    def tearDown(self):
        self.ctx.pop()

    def test_on_error_handler_called(self):
        """POST to endpoint with custom on_error should return JSON error payload."""
        response = self.client.post('/post_with_custom_error')
        self.assertEqual(response.status_code, 400)
        # Ensure response is JSON and contains the expected keys
        data = response.get_json()
        self.assertIsInstance(data, dict)
        self.assertEqual(data.get('status'), 'error')
        self.assertEqual(data.get('message'), 'Validation failed')
        # details should be a dict mapping field -> list containing the validation error message
        self.assertIn('details', data)
        self.assertIsInstance(data['details'], dict)
        self.assertIn('email', data['details'])
        self.assertIsInstance(data['details']['email'], list)
        self.assertIn('Missing form data: email', data['details']['email'])


if __name__ == '__main__':
    unittest.main()
