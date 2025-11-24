from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django_otp.admin import OTPAdminSite

from core.views import AuthenticatedLandingView
from users.urls import urlpatterns as users_urlpatterns

# Solo habilitar OTP si está configurado
if settings.ENABLE_OTP_ADMIN:
    admin.site.__class__ = OTPAdminSite
# admin.autodiscover()
# admin.site.enable_nav_sidebar = False

urlpatterns = [
    path('', AuthenticatedLandingView.as_view(), name='landing'),
    path('admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns.extend(users_urlpatterns)