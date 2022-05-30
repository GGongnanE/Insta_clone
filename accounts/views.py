import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .forms import SignUpForm
from .models import Profile, Follow

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

    return render(request, 'accounts/signup.html', {'form': form})


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

    return render(request, 'accounts/login.html', {'form': form})


# 로그아웃
def logout(request):
    django_logout(request)
    return redirect("/")


# 팔로우
@login_required
@require_POST
def follow(request):
    from_user = request.user.profile
    pk = request.POST.get('pk')
    to_user = get_object_or_404(Profile, pk=pk)
    follow, created = Follow.objects.get_or_create(from_user=from_user, to_user=to_user)

    if created:
        message = '팔로우 시작!'
        status = 1
    else:
        follow.delete()
        message = '팔로우 취소'
        status = 0

    context = {
        'message': message,
        'status': status
    }

    return HttpResponse(json.dumps(context), content_type="application/json")