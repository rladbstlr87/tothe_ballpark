import os
import sys
import django
import pandas as pd
import numpy as np

# Django 환경 설정
sys.path.append('/Users/m2/Desktop/tothe_ballpark')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baseball.settings')
django.setup()

from cal.models import Hitter, Pitcher
from data.make_stat.stat_def import *

hitters = Hitter.objects.all().values()
pitchers = Pitcher.objects.all().values()

h = pd.DataFrame(list(hitters))
p = pd.DataFrame(list(pitchers))

h_num_cols = [col for col in h.columns if h[col].dtype != 'object']
p_num_cols = [col for col in p.columns if p[col].dtype != 'object']

h = preprocessing(h, h_num_cols)
p = preprocessing(p, p_num_cols)

h['power'] = (h['HR']/h['HR'].max()/2 + 0.5).round(3)
h.loc[h['PA'] == 0, 'contact'] = 0
h.loc[h['PA'] != 0, 'contact'] = h['AVG']*0.45 + (1 - h['SO']/h['PA'])*0.2 + h['OBP']*0.2 + (1 - h['GDP']/h['PA'])*0.1 + h['PA']/h['PA'].max()*0.05
h.loc[h['PA'] == 0, 'batting_eye'] = 0
h.loc[h['PA'] != 0, 'batting_eye'] = h['BB']/h['PA']*0.4 - h['SO']/h['PA']*0.2 + h['OBP']*0.4
h['speed'] = (h['SBA']/h['SBA'].max()/2 + 0.5).round(3)

p['stamina'] = p['NP']/p['IP']*0.4 + p['IP']/p['G']*0.4 + p['TBF']/p['IP']*0.2
p['control'] = (p['SO'] / p['IP']) * 0.5 + (1 - p['BB'] / p['IP']) * 0.3 + (1 - p['H'] / p['IP']) * 0.2
p['fireball'] = (p['speed']/p['speed'].max()).round(3)

# inf, -inf를 NaN으로 변환 후, NaN을 0으로
p.replace([np.inf, -np.inf], np.nan, inplace=True)
p.fillna(0, inplace=True)

# 정규화
h['contact'] = (normalize(game_count(h['contact'], h['G']))/2 + 0.5).round(3)
h['batting_eye'] = (normalize(game_count(h['batting_eye'], h['G']))/2 + 0.5).round(3)

p['stamina'] = (normalize(game_count(p['stamina'], p['G']))/2 + 0.5).round(3)
p['control'] = (normalize(game_count(p['control'], p['G']))/2 + 0.5).round(3)

for index, row in h.iterrows():
    Hitter.objects.filter(player_id=row['player_id']).update(
        power=row['power'],
        contact=row['contact'],
        batting_eye=row['batting_eye'],
        speed=row['speed']
    )

for index, row in p.iterrows():
    Pitcher.objects.filter(player_id=row['player_id']).update(
        stamina=row['stamina'],
        control=row['control'],
        fireball=row['fireball']
    )

print("Preprocessing and stat calculation completed. Database updated.")
