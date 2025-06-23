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


# 이미지 gif는 그대로, 이미지는 크기 조절
def handle_uploaded_image(file):
    ext = os.path.splitext(file.name)[-1].lower()

    # GIF는 원본 그대로 저장
    if ext == '.gif':
        return file

    try:
        file.seek(0)  # ✅ 파일 커서 초기화
        img = Image.open(file)

        

        # 최대 크기 제한 (비율 유지)
        img.thumbnail((500, 500))

        buffer = BytesIO()

        # 확장자 → Pillow 포맷 매핑
        format_map = {
            '.jpg': 'JPEG',
            '.jpeg': 'JPEG',
            '.png': 'PNG',
            '.webp': 'WEBP',
        }
        save_format = format_map.get(ext, 'PNG')

        img.save(buffer, format=save_format)

        return ContentFile(buffer.getvalue(), name=file.name)

    except Exception as e:
        print(f"❌ 이미지 처리 에러: {file.name} - {e}")
        return None  # 처리 실패한 건 건너뜀


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
                # 실제 파일 시스템에서도 이미지 삭제
                images_to_delete = PostImage.objects.filter(id__in=delete_ids, post=post)
                for image in images_to_delete:
                    if image.image:  # 이미지 파일이 존재하는지 확인
                        image.image.delete()  # 실제 파일 삭제
                    image.delete()  # DB에서 레코드 삭제

            # 폼 저장
            post = form.save()

            # 새 이미지 추가
            for image in request.FILES.getlist('images'):
                processed = handle_uploaded_image(image)
                if processed:
                    PostImage.objects.create(post=post, image=processed)

            return redirect('posts:detail', id=id)
    else:
        form = PostForm(instance=post)

    return render(request, 'update.html', {'form': form, 'post': post,
        'existing_images': post.images.all()
    })

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

# 직돌이 테스트 
def test_start(request):
    participant_count = TestResult.objects.count()
    return render(request, 'start.html', {
        'participant_count': participant_count,
    })
    
# 직돌이 테스트 질문들
QUESTIONS = [
    {
        "question": "경기 당일 아침, 비 소식 있다면?",
        "choices": ["“환불부터 생각함”", "“비 맞아도 간다. 이것도 직관”"]
    },
    {
        "question": "우리 팀 연패 중인데 오늘 경기 있음",
        "choices": ["“쉴게... 가면 더 질 듯”", "“내가 가서 끊는다 그게 직돌이”"]
    },
    {
        "question": "좌석 고를 때",
        "choices": ["“시야 좋은데서 조용히 야구 관람해야지”", "“응원석에서 같이 뛰어야 진짜지”"]
    },
    {
        "question": "경기 중 오심 발생!",
        "choices": ["“그냥 조용히 넘김”", "“바로 일어나서 야유하기”"]
    },
    {
        "question": "홈런 터졌을 때 반응은?",
        "choices": ["“조용히 박수… (기립은 안 함)”", "“미친!! 으아악!! 자리에서 점프함. 이맛에 직관”"]
    },
    {
        "question": "먹고 싶은 음식 대기 30분",
        "choices": ["“시간 아까워, 경기 봐야지 ”", "“안 먹고 야구 봄? 그건 예의 아님”"]
    },
    {
        "question": "실책으로 실점했을 때",
        "choices": ["“^^... 그럴 수 있지..”", "“와 진짜 미쳤나봐 정떨어져”"]
    },
    {
        "question": "원정팀 응원가가 더 신남",
        "choices": ["“나에겐 우리 팀 응원가만 있음”", "“그건 인정한다. 같이 흥얼거림”"]
    },
    {
        "question": "경기 끝나고 하는 일은?",
        "choices": ["“조용히 퇴장”", "“퇴근길 기다리거나 직관 후기 올림”"]
    },
    {
        "question": "유니폼 고를 때 기준",
        "choices": ["“무난한 거 입자”", "“콜라보 유니폼 + 응원봉 + 헤어밴드 풀셋”"]
    },
    {
        "question": "팬서비스를 받을 기회가 생겼다면?",
        "choices": ["“멀리서 보기만 함”", "“싸인받고 인증까지 찍음”"]
    },
    {
        "question": "직관 중 경기 외의 즐거움은?",
        "choices": ["“스코어링과 데이터 분석”", "“치어리더 응원, 관중 반응 구경”"]
    },
    ]
# 직돌이 점수
SCORE_TABLE = [
                        ['A,B,D,E', 'C'],
                        ['A,D', 'B,C,E'],
                        ['A,D', 'E'],
                        ['A,D', 'E'],
                        ['D', 'B,E'],
                        ['A,C,D', 'B,E'],
                        ['A,D', 'B,C,E'],
                        ['A,D', 'B,E'],
                        ['A,D', 'B,C,E'],
                        ['A,C,D,E', 'B'],
                        ['A,D', 'B,E'],
                        ['A,C,D', 'B'],
                        ['A,D', 'B,E'],
                        ['A', 'B,E'], ]
# 테스트 질문 처리 
def test_question(request, step):
    if step > len(QUESTIONS):
        return redirect('posts:test_result')

    # 세션 초기화 (처음 시작할 때만)
    if step == 1 and request.method == 'GET':
        request.session['type_scores'] = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}

    if request.method == 'POST':
        choice = int(request.POST.get('choice'))  # 0 또는 1
        # 선택된 보기에서 점수 가져오기
        type_code = SCORE_TABLE[step - 1][choice]

        # 세션에 유형별 점수 누적
        type_scores = request.session.get('type_scores', {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0})
        for code in type_code.split(','):
            code = code.strip()
            if code:  # 빈 문자열 무시
                type_scores[code] += 1
        request.session['type_scores'] = type_scores

        return redirect('posts:test_question', step=step + 1)

    q = QUESTIONS[step - 1]
    return render(request, 'test_question.html', {
        'step': step,
        'total': len(QUESTIONS),
        'question': q['question'],
        'choices': q['choices'],
        'progress': int((step / len(QUESTIONS)) * 100),
    })
    
# 테스트 결과 처리
def test_result(request):
    type_scores = request.session.get('type_scores', {})
    if not type_scores:
        return redirect('posts:test_question', step=1)

    # 가장 높은 점수의 유형 찾기
    best_type = max(type_scores, key=type_scores.get)

    # 결과 정보 매핑
    results = {
        'A': {
            'tag': '데이터형직돌이',
        },
        'B': {
            'tag': '덕후형직돌이',
        },
        'C': {
            'tag': '감성형직돌이',
        },
        'D': {
            'tag': '관망형직돌이',
        },
        'E': {
            'tag': '리액션형직돌이',
        },
    }

    result = results.get(best_type, {})
    return render(request, 'result.html', {'result': result})
