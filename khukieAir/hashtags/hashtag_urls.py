from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('', views.HashTagCreateInquire.as_view()),
    path('<int:pk>/', views.HashTagRetrieveDelete.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)