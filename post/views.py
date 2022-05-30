from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .admin import PostForm
from .models import Post

import json
from django.views.decorators.http import require_POST
from django.http import HttpResponse

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

# 신규 포스트 작성
@login_required
def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # post.tag_save()
            messages.info(request, '새 글이 등록되었습니다.')

            return redirect('post:post_list')  # post/post_list 페이지로 이동
    else:
        form = PostForm()
    return render(request, 'post/post_new.html', {
        'form': form
    })

# 포스트 편집
@login_required
def post_edit(request, pk):

    # get_object_or_404 : 모델에서 찾는 요소가 있으면 반환, 없으면 404에러
    # objects.get을 사용 시, 찾는 요소가 없다면 500에러가 발생한다.
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.warning(request, '잘못된 접근입니다.')

        return redirect('post:post_list')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            # post.tag_set.clear()
            # post.tag_save()
            messages.success(request, '수정 완료')

            return redirect('post:post_list')

    else:
        form = PostForm(instance=post)

    return render(request, 'post/post_edit.html', {
        'post' : post,
        'form' : form
    })

# 포스팅 삭제
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user or request.method != 'POST':
        messages.warning(request, '잘못된 접근입니다.')

    else:
        post.delete()
        messages.success(request, '삭제 완료')

    return redirect('post:post_list')


@login_required
@require_POST
def post_like(request):
    pk = request.POST.get('pk', None)
    post = get_object_or_404(Post, pk=pk)
    post_like, post_like_created = post.like_set.get_or_create(user=request.user)

    if not post_like_created:
        post_like.delete()
        message = "좋아요를 취소합니다."
    else:
        message = "좋아요"

    context = {'like_count': post.like_count, 'message': message }

    return HttpResponse(json.dumps(context), content_type="application/json")


@login_required
@require_POST
def post_bookmark(request):
    pk = request.POST.get('pk', None)
    post = get_object_or_404(Post, pk=pk)
    post_bookmark, post_bookmark_created = post.bookmark_set.get_or_create(user=request.user)

    if not post_bookmark_created:
        post_bookmark.delete()
        message = "북마크 취소"
    else:
        message = "북마크"

    context = {'bookmark_count': post.bookmark_count,
               'message': message}

    return HttpResponse(json.dumps(context), content_type="application/json")