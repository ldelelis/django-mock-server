import json
from unittest.mock import (
    patch,
    Mock
)

from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_204_NO_CONTENT
)

from authentication.models import User, OneOffToken
from common.tests.testcases import APIViewSetTestCase


class LoginViewTestCase(APIViewSetTestCase):
    def setUp(self):
        super().setUp()
        self.user_data = {
            "email": "foo@bar.baz",
            "password": "aaaaaa"
        }
        self.url = reverse("login")

    @patch('authentication.views.authenticate')
    def test_fake_user_raises_permission_denied_error(self, patch_authenticate):
        patch_authenticate.return_value = False

        response = self.client.post(self.url, data=self.user_data)

        self.assertEqual(response.status_code, 400)

    @patch('authentication.views.authenticate')
    def test_unhandled_exception_raises_500(self, patch_authenticate):
        patch_authenticate.side_effect = Exception()

        response = self.client.post(self.url, data=self.user_data)

        self.assertEqual(response.status_code, 500)

    @patch('authentication.views.Token.objects')
    @patch('authentication.models.User.objects')
    @patch('authentication.views.authenticate')
    def test_successful_login_returns_token_and_id(self, patch_authenticate, patch_user_manager,
                                                   patch_token_manager):
        mock_user = Mock()
        mock_user.key = 'aaaaaaaaaaaaaaaaaaaaaaaaa'
        mock_user.id = 12345
        patch_authenticate.return_value = mock_user
        patch_user_manager.get.return_value = mock_user
        patch_token_manager.get_or_create.return_value = (mock_user, None)

        response = self.client.post(self.url, data=self.user_data)

        self.assertIn('token', json.loads(response.content))
        self.assertIn('id', json.loads(response.content))


class LogoutViewTestCase(APIViewSetTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_data = {
            "email": "foo@bar.baz",
            "password": "aaaaaa"
        }

    def setUp(self):
        super().setUp()
        self.user = User.objects.create(
            **self.user_data
        )
        self.token = self.user.auth_token
        self.url = reverse("logout")

    def test_successful_logout_destroys_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')

        self.client.post(self.url)

        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(user=self.user)

    def test_non_existent_user_logout_displays_error(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token a9ead5e9d5e9d59eabd4a9ed6a9d7bcad')

        response = self.client.post(self.url)

        self.assertJSONEqual(response.content, {'detail': 'Invalid token.'})


class PasswordResetRequestViewTestCase(APIViewSetTestCase):
    @classmethod
    def setUpClass(cls):
        super(PasswordResetRequestViewTestCase, cls).setUpClass()
        cls.url = reverse('password_reset_request')
        cls.user = cls.create_bare_minimum_tenant()

    def test_junk_data_raises_error(self):
        request_data = {'email': 'aninvalidmail'}

        response = self.client.post(
            self.url,
            data=request_data
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['email'][0]), 'Enter a valid email address.')

    def test_nonexistent_user_returns_404(self):
        request_data = {'email': 'thisuserdoes@not.exist'}

        response = self.client.post(
            self.url,
            data=request_data
        )

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    @patch('authentication.views.mail_reset_request.delay')
    @patch('authentication.models.OneOffToken.objects')
    def test_new_token_is_created(self, patch_token_manager, _):
        patch_token_manager.get_or_create = Mock()
        patch_token_manager.get_or_create.return_value = (Mock(), Mock())
        request_data = {'email': self.user.email}

        self.client.post(
            self.url,
            data=request_data
        )

        patch_token_manager.get_or_create.assert_called_once()

    @patch('authentication.views.mail_reset_request.delay')
    def test_request_mail_is_sent(self, patch_send_mail):
        request_data = {'email': self.user.email}
        token = OneOffToken.objects.create(
            user=self.user
        )

        response = self.client.post(
            self.url,
            data=request_data
        )

        patch_send_mail.assert_called_once_with(self.user.email, token.key)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)


class PasswordResetTestCase(APIViewSetTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('password_reset')

    def test_regular_token_is_allowed(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.tenant.user_ptr.auth_token}')
        request_data = {'new_password': 'foobarbaz'}

        response = self.client.post(
            self.url,
            data=request_data,
        )

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_one_off_token_is_allowed(self):
        one_off_token = OneOffToken.objects.create(
            user=self.tenant.user_ptr
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'MailToken {one_off_token.key}')
        request_data = {'new_password': 'foobarbaz'}

        response = self.client.post(
            self.url,
            data=request_data
        )

        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_unauthenticated_request_is_disallowed(self):
        request_data = {'new_password': 'foobarbaz'}

        response = self.client.post(
            self.url,
            data=request_data
        )

        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
