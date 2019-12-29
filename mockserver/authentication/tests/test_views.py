import json
from unittest.mock import (
    patch,
    Mock
)

from django.test import (
    TestCase,
    Client
)
from rest_framework.authtoken.models import Token

from authentication.models import User


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.user_data = {
            "email": "foo@bar.baz",
            "password": "aaaaaa"
        }

    @patch("authentication.views.authenticate")
    def test_fake_user_raises_permission_denied_error(self, patch_authenticate):
        patch_authenticate.return_value = False

        response = self.c.post('/login', data=self.user_data)

        self.assertEqual(response.status_code, 400)

    @patch("authentication.views.authenticate")
    def test_unhandled_exception_raises_500(self, patch_authenticate):
        patch_authenticate.side_effect = Exception()

        response = self.c.post('/login', data=self.user_data)

        self.assertEqual(response.status_code, 500)

    @patch("authentication.views.Token.objects")
    @patch('authentication.models.User.objects')
    @patch("authentication.views.authenticate")
    def test_successful_login_returns_token_and_id(self, patch_authenticate, patch_user_manager, patch_token_manager):
        mock_user = Mock()
        mock_user.key = 'aaaaaaaaaaaaaaaaaaaaaaaaa'
        mock_user.id = 12345
        patch_authenticate.return_value = mock_user
        patch_user_manager.get.return_value = mock_user
        patch_token_manager.get_or_create.return_value = (mock_user, None)

        response = self.c.post('/login', data=self.user_data)

        self.assertIn('token', json.loads(response.content))
        self.assertIn('id', json.loads(response.content))
