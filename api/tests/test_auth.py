"""
Authentication tests — registration, login, token refresh, edge cases.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User


class RegistrationTests(TestCase):
    """Tests for POST /api/auth/register/"""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/auth/register/'

    def test_register_success(self):
        """A valid registration should return 201 and user data."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPass123',
            'role': 'viewer',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['role'], 'viewer')
        self.assertNotIn('password', response.data)

    def test_register_duplicate_username(self):
        """Duplicate username should return 400."""
        User.objects.create_user(username='existing', password='Test@12345')
        data = {
            'username': 'existing',
            'email': 'new@example.com',
            'password': 'StrongPass123',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        """Duplicate email should return 400."""
        User.objects.create_user(
            username='user1', email='same@test.com', password='Test@12345'
        )
        data = {
            'username': 'user2',
            'email': 'same@test.com',
            'password': 'StrongPass123',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password(self):
        """Password shorter than 8 chars should fail."""
        data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'short',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        """Missing required fields should return 400."""
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_default_role(self):
        """If no role specified, user should default to viewer."""
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'StrongPass123',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['role'], 'viewer')


class LoginTests(TestCase):
    """Tests for POST /api/auth/token/"""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/auth/token/'
        self.user = User.objects.create_user(
            username='loginuser', password='Test@12345', role='admin'
        )

    def test_login_success(self):
        """Valid credentials should return access and refresh tokens."""
        response = self.client.post(self.url, {
            'username': 'loginuser',
            'password': 'Test@12345',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password(self):
        """Wrong password should return 401."""
        response = self.client.post(self.url, {
            'username': 'loginuser',
            'password': 'WrongPassword',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Non-existent user should return 401."""
        response = self.client.post(self.url, {
            'username': 'ghost',
            'password': 'Test@12345',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshTests(TestCase):
    """Tests for POST /api/auth/token/refresh/"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='refreshuser', password='Test@12345'
        )

    def test_refresh_success(self):
        """Valid refresh token should return new access token."""
        login = self.client.post('/api/auth/token/', {
            'username': 'refreshuser',
            'password': 'Test@12345',
        })
        refresh_token = login.data['refresh']
        response = self.client.post('/api/auth/token/refresh/', {
            'refresh': refresh_token,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_refresh_invalid_token(self):
        """Invalid refresh token should fail."""
        response = self.client.post('/api/auth/token/refresh/', {
            'refresh': 'invalid-token-here',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
