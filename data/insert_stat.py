import pandas as pd

def parsing_0(value):
    try:
        if isinstance(value, str) and ' ' in value:
            whole, frac = value.split()
            num, denom = frac.split('/')
            return float(whole) + float(num) / float(denom)
        elif isinstance(value, str) and '/' in value:
            num, denom = value.split('/')
            return float(num) / float(denom)
        else:
            return float(value)
    except:
        return None

h = pd.read_csv('data/all_hitter_stats.csv')
p = pd.read_csv('data/all_pitcher_stats.csv')

h_cols = [
    '선수명', '팀명', 'AVG', 'G', 'PA', 'AB', 'R', 'H',
    '2B', '3B', 'HR', 'TB', 'RBI', 'SAC', 'SF',
    'BB', 'IBB', 'HBP', 'SO', 'GDP',
    'SLG', 'OBP', 'OPS', 'MH', 'RISP', 'PH-BA'
]
p_cols = [
    '선수명', '팀명', 'ERA', 'G', 'W', 'L', 'SV', 'HLD', 'WPCT',
    'IP', 'H', 'HR', 'BB', 'HBP', 'SO', 'R', 'ER', 'WHIP',
    'CG', 'SHO', 'QS', 'BSV', 'TBF', 'NP', 'AVG',
    '2B', '3B', 'SAC', 'SF', 'IBB', 'WP', 'BK', '생일'
]

# 문자열 컬럼 정의
h_str_cols = ['선수명', '팀명']
p_str_cols = ['선수명', '팀명', '생일']

h_num_cols = [col for col in h_cols if col not in h_str_cols]
p_num_cols = [col for col in p_cols if col not in p_str_cols]

# -를 0으로 대체하고 숫자형으로 변환
h[h_num_cols] = h[h_num_cols].replace('-', '0')
h[h_num_cols] = h[h_num_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

# IP(이닝)의 분수표시를 실수로 변경
p[p_num_cols] = p[p_num_cols].replace('-', '0')
p[p_num_cols] = p[p_num_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

# 스탯 조합
# 원본 계산
# h['power'] = ((h['HR']/h['PA']) * (0.6 + (h['SLG'] - h['AVG'])*0.2 + h['IBB']/h['PA']*0.2))
h['power'] = h['HR']/h['HR'].max().round(3) # 3루타까지 추가 반영
h['contact'] = (h['AVG']*0.45 + (1 - h['SO']/h['PA'])*0.2 + h['OBP']*0.2 + (1 - h['GDP']/h['PA'])*0.1 + h['PA'] / h['PA'].max()*0.05)
h['batting_eye'] = (h['BB']/h['PA']*0.4 - h['SO']/h['PA']*0.2 + h['OBP']*0.4)
# 도루 정보 넣기

p['stamina'] = (p['NP']/p['G']*0.4 + p['IP']/p['G']*0.4 + p['TBF']/p['G']*0.2)
p['control'] = (p['SO']/p['G']*0.5 - p['HBP']/p['G']*0.2 - p['H']/p['G']*0.3)

# 주전선수에 가중치 크게 적용
def game_count(series):
    return series * (p['G'] / p['G'].max())
# Min-Max 정규화 함수
def normalize(series):
    return ((series - series.min()) / (series.max() - series.min()))

# 정규화된 스탯 적용
# h['power'] = (normalize(game_count(h['power']))/2 + 0.5).round(3)
h['contact'] = (normalize(game_count(h['contact']))/2 + 0.5).round(3)
h['batting_eye'] = (normalize(game_count(h['batting_eye']))/2 + 0.5).round(3)

p['stamina'] = (normalize(game_count(p['stamina']))/2 + 0.5).round(3)
p['control'] = (normalize(game_count(p['control']))/2 + 0.5).round(3)

# CSV 저장
h.to_csv('data/all_hitter_stats.csv', index=False)
p.to_csv('data/all_pitcher_stats.csv', index=False)