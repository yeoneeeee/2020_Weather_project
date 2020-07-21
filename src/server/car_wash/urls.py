from django.urls import path

from car_wash import views

urlpatterns = [
    path('', views.washer_list, name='washer_list')
]