from django.urls import path

from wscore import views

urlpatterns = [
    path('<str:region>', views.score_list, name='home'),
    path('<str:region>/<str:date>', views.score_detail, name="detail"),
]