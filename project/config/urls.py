from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('chats/', include('apps.chats.urls')),

    path('admin/', admin.site.urls),
    path('api/', include([
        path('v1/', include([
            path('accounts/', include('apps.accounts.api.v1.urls')),
            path('chats/', include('apps.chats.api.v1.urls')),
        ])),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
