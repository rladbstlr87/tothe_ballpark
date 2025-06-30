from django.shortcuts import render, redirect

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

# 직돌이 테스트 점수
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
    ['A', 'B,E'], 
]

# 테스트 질문 처리 
def test_question(request, step):
    if step > len(QUESTIONS):
        return redirect('jikdoltest:test_result')

    if step == 1 and request.method == 'GET':
        request.session['type_scores'] = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}

    if request.method == 'POST':
        choice = int(request.POST.get('choice'))
        # 선택된 보기에서 점수 가져오기
        type_code = SCORE_TABLE[step - 1][choice]

        # 세션에 유형별 점수 누적
        type_scores = request.session.get('type_scores', {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0})
        for code in type_code.split(','):
            code = code.strip()
            if code:
                type_scores[code] += 1
        request.session['type_scores'] = type_scores

        return redirect('jikdoltest:test_question', step=step + 1)

    q = QUESTIONS[step - 1]

    context = {
        'step': step,
        'total': len(QUESTIONS),
        'question': q['question'],
        'choices': q['choices'],
        'progress': int((step / len(QUESTIONS)) * 100),
    }

    return render(request, 'test_question.html', context)

# 사용자의 테스트 결과 
def test_result(request):
    type_scores = request.session.get('type_scores', {})
    if not type_scores:
        return redirect('start')
    best_type = max(type_scores, key=type_scores.get)

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

    result = results.get(best_type)
    template_name = f'result{best_type}.html'
    context = {
        'result': result,
    }
    
    return render(request, template_name, context)

# 공유 링크
def result_share(request, type_code):
    type_code = type_code
    results = {
        'A': {'tag': '데이터형직돌이'},
        'B': {'tag': '덕후형직돌이'},
        'C': {'tag': '감성형직돌이'},
        'D': {'tag': '관망형직돌이'},
        'E': {'tag': '리액션형직돌이'},
    }

    result = results[type_code]
    template_name = f'result{type_code}.html'
    return render(request, template_name, {'result': result})