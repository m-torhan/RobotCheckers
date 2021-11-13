from django.conf.urls import include
from django.urls import path
from django.contrib import admin

urlpatterns = [
    path('checkers/', include('checkers.urls')),
    path('admin/', admin.site.urls),
]