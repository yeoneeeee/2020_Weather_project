from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.core import serializers
from .models import Washer
# Create your views here.


def washer_list(request):
    washer_set = Washer.objects.all()
    data = list(washer_set.values())
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})


