from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    
    # Auth
    path('auth/', include('apps.users.urls')),
    path('accounts/', include('allauth.urls')),
    
    path('marketplace/', include('apps.marketplace.urls')),
    path('freelance/', include('apps.freelance.urls')),
    path('ai/', include('apps.ai_system.urls')),
    path('payments/', include('apps.payments.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('chat/', include('apps.chat.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
