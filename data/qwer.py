import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# 1. 데이터 불러오기
df = pd.read_csv("all_hitter_stats.csv")

# 2. 사용할 스탯 목록
features = [
    'AVG', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'TB', 'RBI', 'SAC', 'SF',
    'BB', 'IBB', 'HBP', 'SO', 'GDP', 'SLG', 'OBP', 'OPS', 'MH', 'RISP',
    'PH-BA', 'SBA', 'SB', 'CS', 'SB%', 'OOB', 'PKO'
]

# 3. 클러스터링 대상: G > 20인 선수
df_cluster = df[df['G'] > 20].copy()
X = df_cluster[features].dropna()
df_cluster = df_cluster.loc[X.index]  # dropna 이후 인덱스 정렬

# 4. 정규화
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 5. KMeans 클러스터링 (군집 5개)
kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
df_cluster['cluster'] = kmeans.fit_predict(X_scaled)

# 6. 클러스터 중심값 계산
cluster_centers = pd.DataFrame(kmeans.cluster_centers_, columns=features)

# 7. 클러스터 중심값 기반 자동 스타일 판단 함수
def classify_cluster_by_center(center):
    power_score = center[['HR', 'SLG', 'OPS', 'TB']].mean()
    contact_score = center[['AVG', 'H', 'MH']].mean() - center['SO'] * 0.1  # 삼진 패널티
    eye_score = center[['BB', 'OBP']].mean()
    speed_score = center[['SB', 'SBA', 'SB%']].mean()

    scores = {
        '파워형': power_score,
        '컨택형': contact_score,
        '선구안형': eye_score,
        '스피드형': speed_score
    }

    return scores

# 8. 클러스터별 점수 분석 → 가장 높은 점수 스타일로 자동 부여
cluster_scores = {i: classify_cluster_by_center(row) for i, row in cluster_centers.iterrows()}

# 스타일 중복 방지하며 자동 부여
cluster_to_style_name = {}
assigned_styles = set()

for cluster_id, score_dict in cluster_scores.items():
    sorted_scores = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)
    for style, _ in sorted_scores:
        if style not in assigned_styles:
            cluster_to_style_name[cluster_id] = style
            assigned_styles.add(style)
            break

# 남은 클러스터는 평범형으로 처리
for cluster_id in range(5):
    if cluster_id not in cluster_to_style_name:
        cluster_to_style_name[cluster_id] = '평범형'

# 9. 스타일 이름 → 코드
style_name_to_code = {
    '파워형': 0,
    '스피드형': 1,
    '컨택형': 2,
    '선구안형': 3,
    '평범형': 4
}

# 10. 스타일 코드 할당
df_cluster['style_code'] = df_cluster['cluster'].map(cluster_to_style_name).map(style_name_to_code)

# 11. G ≤ 20은 평범형
df_rest = df[df['G'] <= 20].copy()
df_rest['style_code'] = 4  # 평범형

# 12. 병합
final_df = pd.concat([df_cluster, df_rest], ignore_index=True)

# 13. 스타일 이름 할당
code_to_style_name = {v: k for k, v in style_name_to_code.items()}
final_df['style_name'] = final_df['style_code'].map(code_to_style_name)

# 14. 스타일별 인원 수 집계
style_counts = final_df['style_name'].value_counts().reset_index()
style_counts.columns = ['스타일', '인원수']

# 15. 결과 저장 및 출력
final_df[['선수명', '팀명', 'G', 'AVG', 'style_code', 'style_name']].sort_values(by='선수명').to_csv("style_classification_result.csv", index=False)
print(style_counts)
