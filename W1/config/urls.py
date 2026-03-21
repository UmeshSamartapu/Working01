from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('patients/', include('apps.patients.urls')),
    path('ecg/', include('apps.ecg.urls')),
    path('results/', include('apps.result.urls')),
    path('reports/', include('apps.reports.urls')),
    path('ar/', include('apps.ar_viz.urls')),
]

# Media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)