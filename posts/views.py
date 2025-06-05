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
    comments = post.comment_set.all().order_by('-created_at')  # 최신순이면 이렇게
    
    
    
    context = {
        'post': post,
        'comments': comments,  # 댓글 목록
        'form': CommentForm(), # 댓글 작성 폼
        
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

# 댓글 수정도 디테일 페이지에서 이루어지도록
@login_required
def comment_update(request, post_id, comment_id):
    comment = Comment.objects.get(id=comment_id)
    real_post_id = comment.post.id # 댓글이 연결된 실제 게시글 id
    
    if request.user != comment.user:
        return redirect('posts:detail', id=real_post_id)
    
    if request.method == 'POST':
        edit_form = CommentForm(request.POST, request.FILES, instance=comment) # 댓글 수정 폼
        if edit_form.is_valid():
            edit_form.save()
            return redirect('posts:detail', id=real_post_id)
    else:
        edit_form = CommentForm(instance=comment)
        
    # 게시글도 같이 넘겨줘야 게시글 상세페이지가 렌더링 가능
    post = Post.objects.get(id=real_post_id)
    comments = post.comment_set.all()  # 댓글 목록
    
    context = {
        'post': post,
        'comments': comments,
        'form': CommentForm(), # 새 댓글 입력용
        'edit_form': edit_form,  # 수정 폼
        'edit_comment_id': comment_id,  # 수정할 댓글의 ID
    }
    
    return render(request, 'detail.html', context)

@login_required
def comment_delete(request, post_id, comment_id):
    comment = Comment.objects.get(id=comment_id)
    
    if request.user == comment.user:
        comment.delete()
    
    return redirect('posts:detail', id =post_id)

@login_required
def post_like(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    
    if user in post.like_users.all():
        post.like_users.remove(user)
    else:
        post.like_users.add(user)
    return redirect('posts:detail', id=post_id)