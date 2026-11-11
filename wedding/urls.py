from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('rsvp.urls')),
]

if settings.DEBUG:
    # Só em desenvolvimento: em produção o Nginx entrega /static/.
    urlpatterns += staticfiles_urlpatterns()
