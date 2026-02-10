from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

class Login(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        user = get_object_or_404(User, username = request.data['username'])
        if not user.check_password(request.data['password']):
            return Response({"detail":"Not found"}, status=status.HTTP_404_NOT_FOUND)
        token, created = Token.objects.get_or_create(user = user)
        serializer = UserSerializer(instance = user)
        return Response({"token":token.key, "user":serializer.data})

class Signup(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username = request.data['username'])
            user.set_password(request.data['password'])
            user.save()
            token = Token.objects.create(user = user)
            return Response({"token":token.key, "user": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TestToken(APIView):
    def get(self, request):
        return Response("passed for {}".format(request.user.email))

class RequestPasswordReset(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            
            # Get frontend URL from environment
            frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5000') 
            absurl = f"{frontend_url}/reset-password/{uidb64}/{token}"
            
            email_body = f"Hello, \n Use the link below to reset your password: \n {absurl}"
            data = {
                'email_body': email_body, 
                'to_email': user.email,
                'email_subject': 'Reset your Password'
            }
            
            try:
                send_mail(
                    data['email_subject'],
                    data['email_body'],
                    'noreply@krishisaarthi.com',
                    [data['to_email']],
                    fail_silently=False,
                )
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
            
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class ResetPassword(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            uidb64 = request.data.get('uidb64')
            token = request.data.get('token')
            password = request.data.get('password')
            
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is invalid or expired'}, status=status.HTTP_401_UNAUTHORIZED)
            
            user.set_password(password)
            user.save()
            return Response({'success': 'Password reset successful'}, status=status.HTTP_200_OK)
            
        except DjangoUnicodeDecodeError as identifier:
             return Response({'error': 'Token is invalid or expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)