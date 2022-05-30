from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .admin import PostForm
from .forms import CommentForm
from .models import Post, Like, Comment, Tag

import json
from django.views.decorators.http import require_POST
from django.http import HttpResponse

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.db.models import Count

'''
    1. 요청이 들어오면 posts 변수에 Post 전부를 저장
    2. 사용자가 로그인 상태일 때, 사용자 이름을 저장 -> 유저 모델 내용을 확인 
    3. 사용자 프로필 저장 -> HTML 렌더링 (유저프로필, 포스트 리스트)
'''


# Create your views here.
def post_list(request, tag=None):
    # Tag 검색에 따른 post_list 가져오기
    if tag:
        # 위에서 받은 태그를 대소문자 구분없이 tag_set_name로 검색한다.
        post_list = Post.objects.filter(tag_set__name__iexact=tag) \
            .prefetch_related('tag_set', 'like_user_set__profile', 'comment_set__author__profile',  # 1:1, 1:N, M:N 가능
                              'author__profile__follower_user', 'author__profile__follower_user__from_user') \
            .select_related('author__profile')  # 1:1의 관계에서만 사용
    else:
        post_list = Post.objects.all() \
            .prefetch_related('tag_set', 'like_user_set__profile', 'comment_set__author__profile',
                              'author__profile__follower_user', 'author__profile__follower_user__from_user') \
            .select_related('author__profile')

    comment_form = CommentForm()
    paginator = Paginator(post_list, 3)
    page_num = request.POST.get('page')

    try:
        posts = paginator.page(page_num)
    except PageNotAnInteger:
        # page 파라미터가 int가 아닌 값이 들어오면 1로 넘겨준다.
        posts = paginator.page(1)
    except EmptyPage:
        # page가 페이지를 넘어서면 마지막 페이지를 넘겨준다.
        posts = paginator.page(paginator.num_pages)

    # Ajax 호출 되었을 경우
    # if request.is_ajax():        <-- # django 4.x에서는 삭제됨.
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return render(request, 'post/post_list_ajax.html', {
            'posts': posts,
            'comment_form': comment_form,
        })

    if request.method == 'POST':
        tag = request.POST.get('tag')
        tag_clean = ''.join(e for e in tag if e.isalnum())

        return redirect('post:post_search', tag_clean)

    if request.user.is_authenticated:
        username = request.user
        user = get_object_or_404(get_user_model(), username=username)
        user_profile = user.profile

        # following
        following_set = request.user.profile.get_following
        following_post_list = Post.objects.filter(author__profile__in=following_set)

        return render(request, 'post/post_list.html', {
            'user_profile': user_profile,
            'posts': posts,
            'comment_form': comment_form,
            'following_post_list': following_post_list
        })
    else:
        return render(request, 'post/post_list.html', {
            'posts': posts,
            'comment_form': comment_form
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
            post.tag_save()
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
        'post': post,
        'form': form
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

    context = {'like_count': post.like_count, 'message': message}

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


'''
    comment(댓글)
    
'''


@login_required
def comment_new(request):
    pk = request.POST.get('pk')  # ajax를 통신하는 부분
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()

            return render(request, 'post/comment_new_ajax.html', {
                'comment': comment
            })

    return redirect('post:post_list')


# 상세페이지에서 댓글 추가 시 사용
@login_required
def comment_new_detail(request):
    pk = request.POST.get('pk')
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()

            return render(request, 'post/comment_new_detail_ajax.html', {
                'comment': comment
            })


@login_required
def comment_delete(request):
    pk = request.POST.get('pk')
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == 'POST' and request.user == comment.author:
        comment.delete()
        message = '삭제완료'
        status = 1

    else:
        message = '잘못된 접근입니다'
        status = 0

    return HttpResponse(json.dumps({'message': message, 'status': status, }), content_type="application/json")
