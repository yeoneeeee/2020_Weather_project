from django.urls import path

from weather import views

urlpatterns = [
    path('<str:region>', views.weather_list, name='home'),
    path('<str:region>/<str:date>', views.weather_detail, name="detail"),
]
