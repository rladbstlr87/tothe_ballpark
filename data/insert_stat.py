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
        return None  # 또는 np.nan

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
h[h_num_cols] = h[h_num_cols].apply(pd.to_numeric, errors='ignore').fillna(0)

# IP(이닝)의 분수표시를 실수로 변경
p[p_num_cols] = p[p_num_cols].replace('-', '0')
p[p_num_cols] = p[p_num_cols].apply(pd.to_numeric, errors='ignore').fillna(0)

# 지표 계산
h['power'] = (h['HR']/h['PA'] + h['SLG'] + h['IBB']/h['PA']).round(3)
h['contact'] = (h['AVG'] - h['SO']/h['PA'] + h['OBP'] - h['GDP']/h['PA']).round(3)
h['batting_eye'] = (h['BB']/h['PA'] - h['SO']/h['PA'] + h['OBP']).round(3)

p['stamina'] = (p['NP']/p['G'] + p['IP']/p['G'] + p['TBF']/p['G']).round(3)
p['control'] = (p['SO']/p['G'] - p['HBP']/p['G'] - p['H']/p['G']).round(3)

# CSV 저장
h.to_csv('data/all_hitter_stats.csv', index=False)
p.to_csv('data/all_pitcher_stats.csv', index=False)