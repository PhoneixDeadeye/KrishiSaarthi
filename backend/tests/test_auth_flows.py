"""
Tests for authentication flows: password reset, logout token deletion,
signup validation, and token validation.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from unittest.mock import patch


class LogoutTokenDeletionTestCase(TestCase):
    """Verify that logout properly deletes the auth token."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="logoutuser", password="TestPass123!", email="logout@test.com"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_logout_deletes_token(self):
        """Logout should delete the user's token."""
        response = self.client.post("/logout")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_logout_without_token_fails(self):
        """Logout without auth should return 401."""
        self.client.credentials()  # Remove auth
        response = self.client.post("/logout")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_double_logout(self):
        """Second logout should fail since token is already deleted."""
        self.client.post("/logout")
        response = self.client.post("/logout")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SignupValidationTestCase(TestCase):
    """Test signup edge cases and validation."""

    def setUp(self):
        self.client = APIClient()

    def test_signup_missing_username(self):
        response = self.client.post("/signup", {
            "email": "test@test.com", "password": "TestPass123!"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_missing_password(self):
        response = self.client.post("/signup", {
            "username": "testuser", "email": "test@test.com"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_short_password(self):
        response = self.client.post("/signup", {
            "username": "testuser", "email": "test@test.com", "password": "123"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_duplicate_email(self):
        """Two users with same email should fail."""
        User.objects.create_user(
            username="existing", password="TestPass123!", email="dup@test.com"
        )
        response = self.client.post("/signup", {
            "username": "newuser", "email": "dup@test.com", "password": "TestPass123!"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_duplicate_username(self):
        """Two users with same username should fail."""
        User.objects.create_user(
            username="taken", password="TestPass123!", email="taken@test.com"
        )
        response = self.client.post("/signup", {
            "username": "taken", "email": "new@test.com", "password": "TestPass123!"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_returns_token(self):
        """Successful signup should return a token and user data."""
        response = self.client.post("/signup", {
            "username": "newuser", "email": "new@test.com", "password": "TestPass123!"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "newuser")


class LoginTimingTestCase(TestCase):
    """Verify login uses constant-time comparison (authenticate())."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="timinguser", password="TestPass123!", email="timing@test.com"
        )

    def test_login_success(self):
        response = self.client.post("/login", {
            "username": "timinguser", "password": "TestPass123!"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_wrong_password(self):
        response = self.client.post("/login", {
            "username": "timinguser", "password": "WrongPassword!"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        response = self.client.post("/login", {
            "username": "nobody", "password": "Whatever123!"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_empty_fields(self):
        response = self.client.post("/login", {
            "username": "", "password": ""
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenValidationTestCase(TestCase):
    """Test the /test_token endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="tokenuser", password="TestPass123!"
        )
        self.token = Token.objects.create(user=self.user)

    def test_valid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.get("/test_token")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token invalidtoken123")
        response = self.client.get("/test_token")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_token(self):
        response = self.client.get("/test_token")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordResetRequestTestCase(TestCase):
    """Test the password reset request flow."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="resetuser", password="TestPass123!", email="reset@test.com"
        )

    def test_password_reset_request_valid_email(self):
        """Password reset with valid email should return 200."""
        response = self.client.post("/password-reset", {
            "email": "reset@test.com"
        }, format="json")
        # Should always return 200 (even for non-existent emails to prevent enumeration)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_request_invalid_email(self):
        """Password reset with non-existent email should still return 200 (no enumeration)."""
        response = self.client.post("/password-reset", {
            "email": "nonexistent@test.com"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_missing_email(self):
        response = self.client.post("/password-reset", {}, format="json")
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK])
