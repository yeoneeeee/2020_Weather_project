from django.urls import path

from accounts import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.kakao_login, name="kakao_login"),
    path('kakao/login/callback', views.kakao_callback, name="kakao_callback"),
    path('kakao/login/logout', views.kakao_logout, name="kakao_logout")
]