from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.Signup.as_view()),
    path('login', views.Login.as_view()),
    path('logout', views.Logout.as_view()),
    path('dropout', views.Dropout.as_view()),
    path('duplicate/<str:id>', views.Duplicate.as_view()),
    path('info', views.Info.as_view()),
    path('findpw', views.Findpw.as_view()),
    path('resetpw', views.Resetpw.as_view()),
]