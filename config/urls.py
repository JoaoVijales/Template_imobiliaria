"""
Root URL configuration for Imobiliária project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Core app (home, about, contact, etc.)
    path("", include(("apps.core.urls", "core"))),
    # Properties app (listings, detail, search, etc.)
    path("imoveis/", include(("apps.properties.urls", "properties"))),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
