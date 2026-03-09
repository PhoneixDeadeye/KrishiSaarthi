from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .health import HealthCheckView, ReadinessCheckView, MetricsView

urlpatterns = [
    path('admin/', admin.site.urls),

    # App-specific routes
    path('field/', include('field.urls')),
    path('finance/', include('finance.urls')),
    path('planning/', include('planning.urls')),
    path('api/', include('chat.urls')),

    # Auth endpoints
    path('login', views.Login.as_view(), name='login'),
    path('signup', views.Signup.as_view(), name='signup'),
    path('test_token', views.TestToken.as_view(), name='test_token'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('password-reset', views.RequestPasswordReset.as_view(), name='password-reset'),
    path('password-reset-confirm', views.ResetPassword.as_view(), name='password-reset-confirm'),
    
    # Health and monitoring endpoints
    path('health', HealthCheckView.as_view(), name='health'),
    path('ready', ReadinessCheckView.as_view(), name='ready'),
    path('metrics', MetricsView.as_view(), name='metrics'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
