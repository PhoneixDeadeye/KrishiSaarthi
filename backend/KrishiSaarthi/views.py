"""
Authentication views for KrishiSaarthi.

Provides login, signup, token test, logout, and password-reset flows.
All public endpoints are rate-limited to prevent brute-force attacks.
"""
from __future__ import annotations

import logging
import os

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import signing
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.utils.encoding import force_str, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .serializers import UserSerializer

logger = logging.getLogger(__name__)


class LoginRateThrottle(AnonRateThrottle):
    """Strict rate limit on login to mitigate brute-force.
    Rate is configured via REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['login']."""
    scope = "login"


class Login(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request) -> Response:
        username: str = request.data.get("username", "").strip()
        password: str = request.data.get("password", "")

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use authenticate() to avoid timing side-channel (constant-time comparison)
        user = authenticate(request=request, username=username, password=password)

        if user is None:
            logger.warning("Failed login attempt for user %s", username)
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"error": "Account is disabled. Contact support."},
                status=status.HTTP_403_FORBIDDEN,
            )

        from knox.models import AuthToken
        instance, token = AuthToken.objects.create(user)
        serializer = UserSerializer(instance=user)
        logger.info("User %s logged in successfully", username)
        return Response({
            "token": token, 
            "expiry": instance.expiry.isoformat() if instance.expiry else None,
            "user": serializer.data
        })


class Signup(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request) -> Response:
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Password validation is now handled inside UserSerializer.validate_password()
        # create_user() is handled inside UserSerializer.create() — no double-save
        user = serializer.save()

        if getattr(settings, "REQUIRE_EMAIL_VERIFICATION", False):
            user.is_active = False
            user.save(update_fields=["is_active"])
            self._send_verification_email(user)
            return Response(
                {
                    "message": "Signup successful. Please verify your email before logging in.",
                    "email_verification_required": True,
                },
                status=status.HTTP_201_CREATED,
            )

        from knox.models import AuthToken
        instance, token = AuthToken.objects.create(user)
        logger.info("New user registered: %s", user.username)
        return Response(
            {
                "token": token, 
                "expiry": instance.expiry.isoformat() if instance.expiry else None,
                "user": UserSerializer(instance=user).data
            },
            status=status.HTTP_201_CREATED,
        )

    def _send_verification_email(self, user: User) -> None:
        token = signing.dumps({"uid": user.id}, salt="email-verification")
        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
        verify_link = f"{frontend_url}/verify-email/{token}"
        send_mail(
            subject="Verify your KrishiSaarthi account",
            message=(
                "Welcome to KrishiSaarthi.\n\n"
                f"Please verify your email by opening this link:\n{verify_link}\n\n"
                "If you did not create this account, you can ignore this email."
            ),
            from_email="noreply@krishisaarthi.com",
            recipient_list=[user.email],
            fail_silently=False,
        )


class TestToken(APIView):
    def get(self, request) -> Response:
        return Response(
            {"message": f"Token valid for {request.user.username}"},
            status=status.HTTP_200_OK,
        )


class Logout(APIView):
    def post(self, request) -> Response:
        try:
            request._auth.delete()
        except AttributeError:
            pass
        except Exception:
            logger.warning("Unexpected error during logout for user %s", request.user.username)
        return Response({"success": "Logged out"}, status=status.HTTP_200_OK)


class RequestPasswordReset(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request) -> Response:
        email = request.data.get("email", "").strip().lower()

        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Always return same message to prevent user enumeration
        success_msg = {"success": "If the email exists, a reset link has been sent."}

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(success_msg, status=status.HTTP_200_OK)

        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)

        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
        reset_link = f"{frontend_url}/reset-password/{uidb64}/{token}"

        try:
            send_mail(
                subject="Reset your KrishiSaarthi password",
                message=f"Hello,\n\nUse this link to reset your password:\n{reset_link}\n\nLink expires in 24 hours.",
                from_email="noreply@krishisaarthi.com",
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as exc:
            logger.error("Password reset email failed for %s: %s", email, exc)
            return Response(
                {"error": "Failed to send reset email. Try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(success_msg, status=status.HTTP_200_OK)


class ResetPassword(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request) -> Response:
        uidb64 = request.data.get("uidb64", "")
        token = request.data.get("token", "")
        password = request.data.get("password", "")

        if not all([uidb64, token, password]):
            return Response(
                {"error": "uidb64, token, and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)
        except (ValueError, User.DoesNotExist):
            return Response(
                {"error": "Token is invalid or expired."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response(
                {"error": "Token is invalid or expired."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            validate_password(password, user=user)
        except DjangoValidationError as exc:
            return Response(
                {"error": "Password too weak.", "details": exc.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(password)
        user.save()
        logger.info("Password reset for user %s", user.username)
        return Response(
            {"success": "Password reset successful."},
            status=status.HTTP_200_OK,
        )


class VerifyEmail(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request) -> Response:
        if not getattr(settings, "REQUIRE_EMAIL_VERIFICATION", False):
            return Response(
                {"message": "Email verification is not required in this environment."},
                status=status.HTTP_200_OK,
            )

        token = request.data.get("token", "")
        if not token:
            return Response(
                {"error": "Verification token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload = signing.loads(token, max_age=60 * 60 * 24, salt="email-verification")
            user = User.objects.get(id=payload.get("uid"))
        except (signing.BadSignature, signing.SignatureExpired, User.DoesNotExist):
            return Response(
                {"error": "Invalid or expired verification token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])

        return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)


class ResendVerification(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request) -> Response:
        if not getattr(settings, "REQUIRE_EMAIL_VERIFICATION", False):
            return Response(
                {"message": "Email verification is not required in this environment."},
                status=status.HTTP_200_OK,
            )

        email = request.data.get("email", "").strip().lower()
        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Enumeration-safe response.
        success_msg = {"message": "If an account exists, a verification email has been sent."}
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(success_msg, status=status.HTTP_200_OK)

        if user.is_active:
            return Response(
                {"message": "Email already verified."},
                status=status.HTTP_200_OK,
            )

        try:
            token = signing.dumps({"uid": user.id}, salt="email-verification")
            frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
            verify_link = f"{frontend_url}/verify-email/{token}"
            send_mail(
                subject="Verify your KrishiSaarthi account",
                message=(
                    "Please verify your email by opening this link:\n"
                    f"{verify_link}"
                ),
                from_email="noreply@krishisaarthi.com",
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as exc:
            logger.error("Failed to resend verification email for %s: %s", email, exc)
            return Response(
                {"error": "Failed to send verification email. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(success_msg, status=status.HTTP_200_OK)