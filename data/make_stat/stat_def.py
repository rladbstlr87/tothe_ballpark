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

max_HR = h['HR'].max() # max를 매번 계산하지 않고 미리 한 번 계산
max_SBA = h['SBA'].max()
def hitter_style(row):
    if (row['HR'] / max_HR) > 0.4:
        return 0  # 홈런 타입
    elif (row['SBA'] / max_SBA) > 0.4:
        return 1  # 스피드 타입
    else:
        return 2  # 컨택 타입

max_velocity = p['velocity'].max()
def pitcher_style(row):
    if (row['velocity'] / max_velocity) > 0.7: # velocity 상위 30%는 파이어볼러 타입이라고 정의
        return 0 # 파이어볼러 타입
    elif row['SO']/row['G']*0.5 + (1 - row['HBP']/row['G']*0.2) + (1 - row['H']/row['G']*0.3) > 0.4:
        return 1 # 제구력 타입
    else:
        return 2 # 무쇠팔 타입