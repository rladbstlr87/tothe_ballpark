import pandas as pd

# CSV 파일을 읽습니다. 파일명은 실제 파일 이름으로 변경하세요.
df = pd.read_csv("kbo_schedule.csv")

# 'stadium' 열의 고유한 값만 추출합니다.
unique_stadiums = df['stadium'].dropna().unique()

# 정렬하여 보기 좋게 출력합니다.
unique_stadiums = sorted(unique_stadiums)

print("경기가 열린 구장 목록:")
for stadium in unique_stadiums:
    print(stadium)