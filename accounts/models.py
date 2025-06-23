from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    KBO_TEAMS = [
        ('', '응원팀을 선택해주세요!'),
        ('SK', 'SSG 랜더스'),
        ('LG', 'LG 트윈스'),
        ('KT', 'KT 위즈'),
        ('NC', 'NC 다이노스'),
        ('OB', '두산 베어스'),
        ('SS', '삼성 라이온즈'),
        ('LT', '롯데 자이언츠'),
        ('WO', '키움 히어로즈'),
        ('HH', '한화 이글스'),
        ('HT', 'KIA 타이거즈'),
    ]

    team = models.CharField(
        max_length=10,
        choices=KBO_TEAMS,
        blank=True,
        null=True,
        verbose_name='My Team',
    )
    nickname = models.CharField(max_length=20, unique=True)

    email = models.EmailField(max_length=254, unique=False, blank=True, null=True)

    profile_image = models.ImageField(upload_to='auth/images/', blank=True, null=True, verbose_name='프로필 이미지', default='')