from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('', views.FileUpload.as_view()),
    path('<int:pk>/', views.FileDetail.as_view()),
    path('<int:pk>/name/', views.FileRename.as_view()),
    path('<int:pk>/path/', views.FileMove.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)