from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from . import views
from .health import HealthCheckView, ReadinessCheckView, MetricsView

urlpatterns = [
    path('admin/', admin.site.urls),

    # App-specific routes
    path('field/', include('field.urls')),
    path('finance/', include('finance.urls')),
    path('planning/', include('planning.urls')),
    path('api/', include('chat.urls')),
    path('api/v1/field/', include('field.urls')),
    path('api/v1/finance/', include('finance.urls')),
    path('api/v1/planning/', include('planning.urls')),
    path('api/v1/chat/', include('chat.urls')),

    # Auth endpoints
    path('login', views.Login.as_view(), name='login'),
    path('signup', views.Signup.as_view(), name='signup'),
    path('test_token', views.TestToken.as_view(), name='test_token'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('password-reset', views.RequestPasswordReset.as_view(), name='password-reset'),
    path('password-reset-confirm', views.ResetPassword.as_view(), name='password-reset-confirm'),
    path('verify-email', views.VerifyEmail.as_view(), name='verify-email'),
    path('resend-verification', views.ResendVerification.as_view(), name='resend-verification'),
    path('api/v1/auth/login', views.Login.as_view(), name='v1-login'),
    path('api/v1/auth/signup', views.Signup.as_view(), name='v1-signup'),
    path('api/v1/auth/test-token', views.TestToken.as_view(), name='v1-test-token'),
    path('api/v1/auth/logout', views.Logout.as_view(), name='v1-logout'),
    path('api/v1/auth/password-reset', views.RequestPasswordReset.as_view(), name='v1-password-reset'),
    path('api/v1/auth/password-reset-confirm', views.ResetPassword.as_view(), name='v1-password-reset-confirm'),
    path('api/v1/auth/verify-email', views.VerifyEmail.as_view(), name='v1-verify-email'),
    path('api/v1/auth/resend-verification', views.ResendVerification.as_view(), name='v1-resend-verification'),
    
    # Health and monitoring endpoints
    path('health', HealthCheckView.as_view(), name='health'),
    path('ready', ReadinessCheckView.as_view(), name='ready'),
    path('metrics', MetricsView.as_view(), name='metrics'),
    path('api/v1/health', HealthCheckView.as_view(), name='v1-health'),
    path('api/v1/ready', ReadinessCheckView.as_view(), name='v1-ready'),
    path('api/v1/metrics', MetricsView.as_view(), name='v1-metrics'),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
