from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    KBO_TEAMS = [
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