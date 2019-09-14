from django.conf.urls import url
from django.contrib import admin
from django.urls import include

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('users.urls')),
    url('api-auth/', include('rest_framework.urls')),
]
