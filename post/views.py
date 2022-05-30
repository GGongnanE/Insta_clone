from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from .models import Post

'''
    1. 요청이 들어오면 posts 변수에 Post 전부를 저장
    2. 사용자가 로그인 상태일 때, 사용자 이름을 저장 -> 유저 모델 내용을 확인 
    3. 사용자 프로필 저장 -> HTML 렌더링 (유저프로필, 포스트 리스트)
'''
# Create your views here.
def post_list(request):
    posts = Post.objects.all()

    if request.user.is_authenticated:
        username = request.user
        user = get_object_or_404(get_user_model(), username=username)
        user_profile = user.profile

        return render(request, 'post/post_list.html', {
            'user_profile': user_profile,
            'posts': posts
        })
    else:
        return render(request, 'post/post_list.html', {
            'posts': posts
        })