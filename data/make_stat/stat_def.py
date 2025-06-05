import pandas as pd

h = pd.read_csv('../all_hitter_stats.csv')
p = pd.read_csv('../all_pitcher_stats.csv')

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

# 주전선수에 가중치 크게 적용
def game_count(series, g_series):
    return series * (g_series / g_series.max())
# Min-Max 정규화 함수
def normalize(series):
    return ((series - series.min()) / (series.max() - series.min()))

# 문자형 컬럼은 그대로 두고 숫자형 컬럼만 골라서 반환
def num_cols(cols, str_cols):
    result = []
    for col in cols:
        if col not in str_cols:
            result.append(col)
    return result

def preprocessing(df, cols):
    df[cols] = df[cols].replace('-', '0')
    df[cols] = df[cols].apply(pd.to_numeric, errors='coerce').fillna(0)
    return df

# h_num_cols = [col for col in h_cols if col not in h_str_cols]
# p_num_cols = [col for col in p_cols if col not in p_str_cols]

# def hitter_style(row):
#     if row['power'] > 0.65:
#         return 0  # 홈런 타입
#     elif row['speed'] > 0.65:
#         return 1  # 스피드 타입
#     elif row['contact'] > 0.65 and row['AVG'] > 0.25:
#         return 2  # 컨택 타입
#     elif row['batting_eye'] > 0.65:
#         return 3 # 선구안 타입
#     else:
#         return 4 # 노말 타입
    
def hitter_style(row):
    avg_stat = (row['power'] + row['speed'] + row['contact'] + row['batting_eye']) / 4
    max_stat = max(row['power'], row['speed'], row['contact'], row['batting_eye'])
    
    if avg_stat < 0.6:
        return 4 # 노말 타입
    elif max_stat == row['contact']:
        if row['AVG'] > 0.245:
            return 2  # 컨택 타입
        else:
            secondary_stat = max(row['power'], row['speed'], row['batting_eye'])
            if row['power'] > 0.6:
                return 0  # 홈런 타입
            elif row['speed'] > 0.6:
                return 1 # 스피드 타입
            else:
                return 3  # 선구안 타입
    elif row['power'] > 0.6:
        return 0  # 홈런 타입
    elif row['speed'] > 0.6:
        return 1 # 스피드 타입
    else:
        return 3 # 선구안 타입

def pitcher_style(row):
    if row['speed'] >= 148:
        return 0 # 파이어볼러 타입
    elif row['control'] > 0.75:
        return 1 # 제구력 타입
    elif row['stamina'] > 0.65:
        return 2 # 무쇠팔 타입
    else:
        return 3 # 노말 타입
