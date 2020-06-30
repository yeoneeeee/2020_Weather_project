from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.


def weather_list(request):
    return JsonResponse({"index": "test"})


def weather_detail(request, date):
    return JsonResponse({"detail": date})
