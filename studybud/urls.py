
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
#create home

    
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),

]
