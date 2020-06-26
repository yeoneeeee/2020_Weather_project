from django.urls import path

from weather import views

urlpatterns = [
    path('', views.weather_list, name='home'),
    path('<int:date>', views.weather_detail, name="detail"),
]