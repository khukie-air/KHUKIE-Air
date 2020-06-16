from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('', views.FileUploadLinkCreate.as_view()),
    path('<int:pk>/', views.FileRetrieveCopyDelete.as_view()),
    path('<int:pk>/info/', views.FileInfoView.as_view()),
    path('<int:pk>/name/', views.FileRename.as_view()),
    path('<int:pk>/path/', views.FileMove.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)