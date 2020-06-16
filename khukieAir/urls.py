"""khukieAir URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^files/', include('khukieAir.S3App.file_urls')),
    url(r'^folders/', include('khukieAir.S3App.folder_urls')),
    url(r'^trash/', include('khukieAir.S3App.trash_urls')),
    url(r'^hashtags/', include('khukieAir.hashtags.hashtag_urls')),
    path('api/auth/', include('khukieAir.UserApp.urls')),
]
