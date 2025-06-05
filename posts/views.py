from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import PostForm, CommentForm

# 게시글 리스트
def post_index(request):
    posts = Post.objects.all().order_by('-created_at')
    total = posts.count()
    posts_with_number = [(total - idx, post) for idx, post in enumerate(posts)]
    context = {
        'posts': posts,
        'posts_with_number': posts_with_number,
        'form': CommentForm(),
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
@login_required
def detail(request, id):
    post = get_object_or_404(Post, id=id)
    comments = post.comment_set.all().order_by('-created_at')
    context = {
        'post': post,
        'comments': comments,
        'form': CommentForm(),
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

# 게시글 좋아요
@login_required
def post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.like_users.all():
        post.like_users.remove(request.user)
    else:
        post.like_users.add(request.user)
    return redirect('posts:detail', id=post_id)
