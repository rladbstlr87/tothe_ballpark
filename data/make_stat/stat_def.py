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