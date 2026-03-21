from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('apps.dashboard.urls')),  # ✅ FIX HERE

    path('accounts/', include('apps.accounts.urls')),
    path('patients/', include('apps.patients.urls')),
    path('ecg/', include('apps.ecg.urls')),
    path('results/', include('apps.results.urls')),
    path('reports/', include('apps.reports.urls')),
    path('ar/', include('apps.ar_viz.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)