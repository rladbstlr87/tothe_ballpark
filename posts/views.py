from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os

# 업로드된 이미지 처리 함수
def handle_uploaded_image(file):
    ext = os.path.splitext(file.name)[-1].lower()
    if ext == '.gif': # gif는 원본 유지
        return file

    file.seek(0)
    img = Image.open(file)
    img.thumbnail((500, 500)) # 500x500 이하로 리사이징 후 저장
    buffer = BytesIO()
    format_map = {
        '.jpg': 'JPEG',
        '.jpeg': 'JPEG',
        '.png': 'PNG',
        '.webp': 'WEBP',
    }
    save_format = format_map.get(ext, 'PNG')
    img.save(buffer, format=save_format)

    return ContentFile(buffer.getvalue(), name=file.name)

# 게시글 리스트
def post_index(request):
    posts = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total = posts.count()
    start_index = total - ((page_obj.number-1) * paginator.per_page)  # 역순으로 1번 글이 가장 마지막 번호
    posts_with_number = [(start_index - idx, post) for idx, post in enumerate(page_obj)]

    context = {
        'posts': posts,
        'posts_with_number': posts_with_number,
        'form': CommentForm(),
        'page_obj': page_obj,
    }

    return render(request, 'post_index.html', context)

# 게시글 생성
@login_required
def create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            
            # 이미지 여러 장 저장 
            images = request.FILES.getlist('images')
            for image in images:
                processed = handle_uploaded_image(image)
                if processed:
                    PostImage.objects.create(post=post, image=processed)
            return redirect('posts:detail', id=post.id)
        
    else:
        form = PostForm()
    return render(request, 'create.html', {'form': form})

# 게시글 상세페이지
def detail(request, id):
    post = get_object_or_404(Post, id=id)
    posts = Post.objects.all().order_by('-created_at')
    total = posts.count()
    posts_with_number = [(total - idx, p) for idx, p in enumerate(posts)]
    paginator = Paginator(posts_with_number, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    comments = post.comment_set.all().order_by('-created_at')
    is_post_updated = post.updated_at.replace(microsecond=0) != post.created_at.replace(microsecond=0)
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
        'total':total,
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
            # 폼 저장 전에 이미지 삭제 처리
            delete_ids = request.POST.getlist('delete_images')
            if delete_ids:
                images_to_delete = PostImage.objects.filter(id__in=delete_ids, post=post)
                for image in images_to_delete:
                    if image.image:
                        image.image.delete()
                    image.delete()
            post = form.save()

            # 새 이미지 추가
            for image in request.FILES.getlist('images'):
                processed = handle_uploaded_image(image)
                if processed:
                    PostImage.objects.create(post=post, image=processed)
            return redirect('posts:detail', id=id)
    else:
        form = PostForm(instance=post)

    context = {
        'form': form,
        'post': post,
        'existing_images': post.images.all(),
    }

    return render(request, 'update.html', context)

# 게시글 삭제
@login_required
def delete(request, id):
    post = get_object_or_404(Post, id=id)
    if request.user == post.user:
        post.delete()
    return redirect('posts:post_index')

# 댓글 생성
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
def comment_update(request, comment_id):
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
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.like_users.all():
        post.like_users.remove(user)
    else:
        post.like_users.add(user)
    return redirect('posts:detail', id=post_id)

# 댓글 좋아요
@login_required
def comment_like(request, comment_id):
    user = request.user
    comment = Comment.objects.get(id=comment_id)
    
    if user in comment.like_users.all():
        comment.like_users.remove(user)
    else:
        comment.like_users.add(user)
    return redirect('posts:detail', id=comment.post.id)

# 게시글 좋아요 비동기 처리
@login_required
def like_async(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)

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

# 댓글 좋아요 비동기 처리
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

    context = {
        'status': status,
        'count': comment.like_users.count(),
    }
    
    return JsonResponse(context)