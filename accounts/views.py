from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import  logout as django_logout
from django.contrib.auth.forms import AuthenticationForm

from .forms import SignUpForm

# Create your views here.

# views.py : 사용자가 URL을 통해 접근했을 때, 구체적으로 어떤 일을 수행할지 결정(컨트롤러 역할)

# 회원 가입
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            return redirect('accounts:login')
    else:
        # 회원가입 페이지를 다시 렌더링
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form' : form })


# 로그인
def login_check(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("/")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form' : form })


# 로그아웃
def logout(request):
    django_logout(request)
    return redirect("/")
