import pandas as pd

# CSV 파일 경로
file_path = 'hitters_records.csv'  # 현재 경로 기준

# CSV 파일 불러오기
df = pd.read_csv(file_path)

# player_id를 먼저 숫자형(int)으로 변환 -> 그다음 문자열(str)로 변환
df['player_id'] = pd.to_numeric(df['player_id'], errors='coerce').dropna().astype(int).astype(str)

# 공백/NaN 필터링
df_cleaned = df[df['player_id'].str.strip().ne('') & df['player_id'].str.lower().ne('nan')]

# 같은 파일에 덮어쓰기
df_cleaned.to_csv(file_path, index=False, encoding='utf-8-sig')
