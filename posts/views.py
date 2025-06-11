from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator
from django.http import JsonResponse

# 게시글 리스트
def post_index(request):
    posts = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total = posts.count()
    start_index = total - ((page_obj.number-1) * paginator.per_page)  # 시작 인덱스 계산  (역순으로 1번 글이 가장 마지막 번호)
    posts_with_number = [(start_index - idx, post) for idx, post in enumerate(page_obj)]
    context = {
        'posts': posts,
        'posts_with_number': posts_with_number,
        'form': CommentForm(),
        'page_obj': page_obj,
    }
    return render(request, 'post_index.html', context)

# 게시글 작성
@login_required
def create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('posts:detail', id=post.id)
    else:
        form = PostForm()
    return render(request, 'create.html', {'form': form})

# 게시글 상세
def detail(request, id):
    post = get_object_or_404(Post, id=id)
    posts = Post.objects.all().order_by('-created_at')
    total = posts.count()
    posts_with_number = [(total - idx, p) for idx, p in enumerate(posts)]
    paginator = Paginator(posts_with_number, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    comments = post.comment_set.all().order_by('-created_at')

    # 게시글 수정 여부
    is_post_updated = post.updated_at.replace(microsecond=0) != post.created_at.replace(microsecond=0)

    # 댓글 객체에 is_updated 속성 직접 추가
    for comment in comments:
        comment.is_updated = comment.updated_at.replace(microsecond=0) != comment.created_at.replace(microsecond=0)

    context = {
        'post': post,
        'posts': posts,
        'posts_with_number': posts_with_number,
        'comments': comments,
        'form': CommentForm(),
        'is_post_updated': is_post_updated,
        'page_obj': page_obj,
    }
    return render(request, 'detail.html', context)

# 게시글 수정
@login_required
def update(request, id):
    post = get_object_or_404(Post, id=id)

    if request.user != post.user:
        return redirect('posts:detail', id=id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:detail', id=id)
    else:
        form = PostForm(instance=post)

    return render(request, 'update.html', {'form': form})

# 게시글 삭제
@login_required
def delete(request, id):
    post = get_object_or_404(Post, id=id)
    if request.user == post.user:
        post.delete()
    return redirect('posts:post_index')

# 댓글 작성
@login_required
def comment_create(request, post_id):
    form = CommentForm(request.POST, request.FILES)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post_id = post_id
        comment.user = request.user
        comment.save()
    return redirect('posts:detail', id=post_id)

# 댓글 수정
@login_required
def comment_update(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post = comment.post

    if request.user != comment.user:
        return redirect('posts:detail', id=post.id)

    if request.method == 'POST':
        edit_form = CommentForm(request.POST, request.FILES, instance=comment)
        if edit_form.is_valid():
            edit_form.save()
            return redirect('posts:detail', id=post.id)
    else:
        edit_form = CommentForm(instance=comment)

    comments = post.comment_set.all().order_by('-created_at')
    context = {
        'post': post,
        'comments': comments,
        'form': CommentForm(),
        'edit_form': edit_form,
        'edit_comment_id': comment_id,
    }
    return render(request, 'detail.html', context)

# 댓글 삭제
@login_required
def comment_delete(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.user:
        comment.delete()
    return redirect('posts:detail', id=post_id)

# 게시글 좋아요 기능
@login_required
def post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.like_users.all():
        post.like_users.remove(request.user)
    else:
        post.like_users.add(user)
    return redirect('posts:detail', id=post_id)

# 댓글 좋아요 기능
@login_required
def comment_like(request, comment_id):
    user = request.user
    comment = Comment.objects.get(id=comment_id)
    
    if user in comment.like_users.all():
        comment.like_users.remove(user)
    else:
        comment.like_users.add(user)
    return redirect('posts:detail', id=comment.post.id)


# 게시물 좋아요 js 기능
@login_required
def like_async(request, id):
    user = request.user
    post = Post.objects.get(id=id)

    if user in post.like_users.all():
        post.like_users.remove(user)
        status = False
    else:
        post.like_users.add(user)
        status = True

    context = {
        'post_id': id,
        'status': status,
        'count': len(post.like_users.all())
    }
    return JsonResponse(context)

# 댓글 좋아요 js 기능
@login_required
def comment_like_async(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    user = request.user

    if user in comment.like_users.all():
        comment.like_users.remove(user)
        status = False
    else:
        comment.like_users.add(user)
        status = True

    return JsonResponse({
        'status': status,
        'count': comment.like_users.count(),
    })
