from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.core import serializers

from .forms import PostForm
from .models import Washer
# Create your views here.


def washer_list(request):

    if request.method == "GET":
        washer_set = Washer.objects.all()
        data = list(washer_set.values())
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})

    elif request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():  # 폼 검증 메소드
            washer = form.save(commit=False)  # lotto 오브젝트를 form으로 부터 가져오지만, 실제로 DB반영은 하지 않는다.
            washer.save()
            return HttpResponse(washer.name)  # url의 name을 경로대신 입력한다.




