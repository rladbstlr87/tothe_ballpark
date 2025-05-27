from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    KBO_TEAMS = [
        ('SSG', 'SSG 랜더스'),
        ('LG', 'LG 트윈스'),
        ('KT', 'KT 위즈'),
        ('NC', 'NC 다이노스'),
        ('두산', '두산 베어스'),
        ('삼성', '삼성 라이온즈'),
        ('롯데', '롯데 자이언츠'),
        ('키움', '키움 히어로즈'),
        ('한화', '한화 이글스'),
        ('KIA', 'KIA 타이거즈'),
    ]

    team = models.CharField(
        max_length=10,
        choices=KBO_TEAMS,
        blank=True,
        null=True,
        verbose_name='응원팀'
    )
    nickname = models.CharField(max_length=20, unique=True)