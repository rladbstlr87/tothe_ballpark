from django.shortcuts import render, redirect
from .models import *
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required


# Create your views here.

def post_index(request):
    posts = Post.objects.all().order_by('-created_at')
    form = CommentForm()
    context = {
        'posts': posts,
        'form': form,
    }
    
    return render(request, 'post_index.html', context)

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
    
    context = {
        'form': form,
        
    }
    
    return render(request, 'create.html', context)

@login_required
def detail(request, id):
    post = Post.objects.get(id=id)
    form = CommentForm()
    
    
    
    context = {
        'post': post,
        'form': form,
        
    }
    
    return render(request, 'detail.html', context)

@login_required
def update(request, id):
    post = Post.objects.get(id=id)
    
    if request.user != post.user:
        return redirect('posts:detail')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:detail', id=id)
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
    }
    
    return render(request, 'update.html', context)
    
@login_required
def delete(request, id):
    post = Post.objects.get(id=id)
    
    if request.user == post.user:
        post.delete()
    
    return redirect('posts:post_index')

@login_required
def comment_create(request, post_id):
    form = CommentForm(request.POST, request.FILES)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post_id = post_id
        comment.user = request.user
        comment.save()
        return redirect('posts:detail', id=post_id)

@login_required
def comment_update(request, post_id, comment_id):
    comment = Comment.objects.get(id=comment_id)
    real_post_id = comment.post.id # 댓글이 연결된 실제 게시글 id
    
    if request.user != comment.user:
        return redirect('posts:detail', id=real_post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('posts:detail', id=real_post_id)
    else:
        form = CommentForm(instance=comment)
    
    context = {
        'form': form,
    }
    
    return render(request, 'comment_update.html', context)

@login_required
def comment_delete(request, post_id, comment_id):
    comment = Comment.objects.get(id=comment_id)
    
    if request.user == comment.user:
        comment.delete()
    
    return redirect('posts:detail', id =post_id)

@login_required
def like(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    
    if user in post.like_users.all():
        post.like_users.remove(user)
    else:
        post.like_users.add(user)
    return redirect('posts:post_index')