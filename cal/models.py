from django.db import models
from django.conf import settings

class Game(models.Model):
    date = models.DateField(max_length = 100)
    time = models.TimeField(max_length = 100)
    team1 = models.CharField(max_length = 100)
    team2 = models.CharField(max_length = 100)
    team1_score = models.IntegerField(null=True, blank=True)
    team2_score = models.IntegerField(null=True, blank=True)
    team1_result = models.CharField(max_length = 100)
    team2_result = models.CharField(max_length = 100)
    stadium = models.CharField(max_length = 100)
    note = models.CharField(max_length=100, null=True, blank=True)
    
    attendance_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='attendance_game',
    )

class Hitter(models.Model):
    player_id = models.CharField(max_length=50, unique=True, primary_key=True, blank=True) # KBO 등록번호 5자리
    player_name = models.CharField(max_length=100)
    team_name = models.CharField(max_length=100)
    AVG = models.FloatField()  # 타율
    G = models.PositiveIntegerField()  # 경기 수
    PA = models.PositiveIntegerField()  # 타석
    AB = models.PositiveIntegerField()  # 타수
    R = models.PositiveIntegerField()  # 득점
    H = models.PositiveIntegerField()  # 안타
    H_2B = models.PositiveIntegerField()  # 2루타
    H_3B = models.PositiveIntegerField()  # 3루타
    HR = models.PositiveIntegerField()  # 홈런
    TB = models.PositiveIntegerField()  # 루타
    RBI = models.PositiveIntegerField()  # 타점
    SAC = models.PositiveIntegerField()  # 희생타
    SF = models.PositiveIntegerField()  # 희생플라이
    BB = models.PositiveIntegerField()  # 볼넷
    IBB = models.PositiveIntegerField()  # 고의사구
    HBP = models.PositiveIntegerField()  # 몸에 맞는 공
    SO = models.PositiveIntegerField()  # 삼진
    GDP = models.PositiveIntegerField()  # 병살타
    SLG = models.FloatField()  # 장타율
    OBP = models.FloatField()  # 출루율
    OPS = models.FloatField()  # OPS
    MH = models.PositiveIntegerField()  # 멀티히트 (추정)
    RISP = models.FloatField()  # 득점권 타율
    PH_BA = models.FloatField()  # 대타 타율 (PH-BA)
    SBA = models.PositiveIntegerField()  # 도루 시도
    SB = models.PositiveIntegerField()  # 도루 성공
    CS = models.PositiveIntegerField()  # 도루 실패
    power = models.FloatField()  # 파워 (평가값일 경우 Integer로)
    contact = models.FloatField()  # 컨택트
    batting_eye = models.FloatField()  # 선구안
    speed = models.FloatField()  # 스피드
    style = models.IntegerField()  # 선수 스타일 (ex: contact hitter 등)

class Pitcher(models.Model):
    player_id = models.CharField(max_length=50, unique=True, primary_key=True, blank=True)
    player_name = models.CharField(max_length=100)  # 선수명
    team_name = models.CharField(max_length=100)  # 팀명
    ERA = models.FloatField()  # 평균 자책점
    G = models.PositiveIntegerField()  # 경기 수
    W = models.PositiveIntegerField()  # 승
    L = models.PositiveIntegerField()  # 패
    SV = models.PositiveIntegerField()  # 세이브
    HLD = models.PositiveIntegerField()  # 홀드
    WPCT = models.FloatField()  # 승률
    IP = models.FloatField()  # 이닝 (소수점까지 입력되는 경우가 많음)
    H = models.PositiveIntegerField()  # 피안타
    HR = models.PositiveIntegerField()  # 피홈런
    BB = models.PositiveIntegerField()  # 볼넷
    HBP = models.PositiveIntegerField()  # 사구
    SO = models.PositiveIntegerField()  # 탈삼진
    R = models.PositiveIntegerField()  # 실점
    ER = models.PositiveIntegerField()  # 자책점
    WHIP = models.FloatField()  # 이닝당 출루 허용 (WHIP)
    CG = models.PositiveIntegerField()  # 완투
    SHO = models.PositiveIntegerField()  # 완봉
    QS = models.PositiveIntegerField()  # 퀄리티스타트
    BSV = models.PositiveIntegerField()  # 블론세이브
    TBF = models.PositiveIntegerField()  # 상대 타자 수
    NP = models.PositiveIntegerField()  # 투구 수
    AVG = models.FloatField()  # 피안타율
    H_2B = models.PositiveIntegerField()  # 피 2루타
    H_3B = models.PositiveIntegerField()  # 피 3루타
    SAC = models.PositiveIntegerField()  # 희생번트 허용
    SF = models.PositiveIntegerField()  # 희생플라이 허용
    IBB = models.PositiveIntegerField()  # 고의4구
    WP = models.PositiveIntegerField()  # 폭투
    BK = models.PositiveIntegerField()  # 보크
    speed = models.IntegerField()  # 구속
    stamina = models.FloatField()  # 체력
    control = models.FloatField()  # 제구력
    fireball = models.FloatField()  # 파이어볼러 수치 (또는 fastball strength 등)
    style = models.IntegerField()  # 투수 스타일

class Stadium(models.Model):
    stadium = models.CharField(max_length=50, unique=True, primary_key=True, blank=True)

class Seat(models.Model):
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE)
    seat_name = models.CharField(max_length=50)
    note = models.CharField(max_length=200)

class Parking(models.Model):
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE)
    parking_name = models.CharField(max_length=50)
    adress = models.CharField(max_length=100)
    note = models.CharField(max_length=200)

class Restaurant(models.Model):
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE)
    restaurant_name = models.CharField(max_length=50)
    adress = models.CharField(max_length=100)
    note = models.CharField(max_length=200)

class Lineup(models.Model):
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE, null=True, blank=True)
    hitter = models.ForeignKey(Hitter, on_delete=models.CASCADE, null=True, blank=True)
    pitcher = models.ForeignKey(Pitcher, on_delete=models.CASCADE, null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)
    batting_order = models.PositiveIntegerField(null=True, blank=True)

class Hitter_Daily(models.Model):
    game_id = models.ForeignKey(Game, on_delete=models.CASCADE)
    date = models.DateField(max_length = 100)
    player = models.ForeignKey(Hitter, on_delete=models.CASCADE, to_field='player_id')
    team = models.CharField(max_length=50)
    AB = models.PositiveIntegerField()
    R = models.PositiveIntegerField()
    H = models.PositiveIntegerField()
    RBI = models.PositiveIntegerField()
    HR = models.PositiveIntegerField()
    BB = models.PositiveIntegerField()
    SO = models.PositiveIntegerField()
    SB = models.PositiveIntegerField()

class Pitcher_Daily(models.Model):
    game_id = models.ForeignKey(Game, on_delete=models.CASCADE)
    date = models.DateField(max_length = 100)
    player = models.ForeignKey(Pitcher, on_delete=models.CASCADE, to_field='player_id')
    team = models.CharField(max_length=50)
    IP = models.FloatField()
    H = models.PositiveIntegerField()
    R = models.PositiveIntegerField()
    ER = models.PositiveIntegerField()
    BB = models.PositiveIntegerField()
    SO = models.PositiveIntegerField()
    HR = models.PositiveIntegerField()
    BF = models.PositiveIntegerField()
    AB = models.PositiveIntegerField()
    NP = models.PositiveIntegerField()