import os
import requests

from django.shortcuts import render, redirect


# Create your views here.

def index(request):
    return render(request, 'login/index.html')


def kakao_login(request):
    address = os.environ.get("IP")+':8000'
    kakao_key = os.environ.get("API_KEY")
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={kakao_key}&redirect_uri=http://{address}/kakao/login/callback&response_type=code"
    )

def kakao_callback(request):
    address = os.environ.get("IP")+':8000'
    kakao_key = os.environ.get("API_KEY")
    user_token = request.GET.get("code")
    token_request = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={kakao_key}"
        f"&redirect_uri=http://{address}/kakao/login/callback&code={user_token}"
    )
    token_response_json = token_request.json()
    error = token_response_json.get("error", None)
    # if there is an error from token_request
    if error is not None:
        return redirect('index')

    access_token = token_response_json.get("access_token")
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    print(profile_request)
    profile_json = profile_request.json()
    nickname = profile_json['properties']['nickname']
    response = render(request, 'login/login.html', {"name": nickname})
    response.set_cookie('access_token', access_token)
    return response


def kakao_logout(request):
    access_token = request.COOKIES.get('access_token')

    if access_token is None:
        return render(request, 'login/index.html')

    requests.post(
        "https://kapi.kakao.com/v1/user/logout",
         headers={"Authorization": f"Bearer {access_token}"},
    )

    response = render(request, 'login/index.html', {"alert":"로그아웃 되었습니다."})
    response.delete_cookie(access_token)
    return response
