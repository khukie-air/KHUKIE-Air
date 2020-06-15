from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('', views.FolderCreate.as_view()),
    path('<int:pk>/', views.FolderRetrieveCopyDelete.as_view()),
    path('<int:pk>/items/', views.FolderItemList.as_view()),
    path('<int:pk>/name/', views.FolderRename.as_view()),
    path('<int:pk>/path/', views.FolderMove.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)