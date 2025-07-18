import os
import sys
import django
import pandas as pd

# Django 환경 설정
sys.path.append('/Users/m2/Desktop/tothe_ballpark')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baseball.settings')
django.setup()

from cal.models import Hitter, Pitcher
from data.make_stat.stat_def import hitter_style, pitcher_style

# --- 데이터베이스에서 데이터 로드 ---
hitters = Hitter.objects.all().values()
pitchers = Pitcher.objects.all().values()

h = pd.DataFrame(list(hitters))
p = pd.DataFrame(list(pitchers))

# --- 선수 스타일 계산 ---
h['style'] = h.apply(hitter_style, axis=1)
p['style'] = p.apply(pitcher_style, axis=1)

# --- 계산된 스타일을 데이터베이스에 업데이트 ---
for index, row in h.iterrows():
    Hitter.objects.filter(player_id=row['player_id']).update(style=row['style'])

for index, row in p.iterrows():
    Pitcher.objects.filter(player_id=row['player_id']).update(style=row['style'])

print("Player styles calculated and updated in the database.")