import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)

df = pd.read_csv('data/all_pitcher_stats.csv')
player_ids = df['player_id'].dropna().astype(int).tolist()

results = []

for pid in player_ids:
    url = f"https://m.sports.naver.com/player/index?from=sports&playerId={pid}&category=kbo&tab=record"
    driver.get(url)
    time.sleep(2.5)

    try:
        # 테이블 헤더들 찾기
        ths = driver.find_elements(By.CSS_SELECTOR, '#record_04 > div > div > table > thead > tr > th')

        # 직구 위치 찾기
        fastball_idx = None
        for idx, th in enumerate(ths):
            if '직구' in th.text:
                fastball_idx = idx + 1
                break

        # 직구 없으면 투심 위치 찾기
        if fastball_idx is None:
            for idx, th in enumerate(ths):
                if '투심' in th.text:
                    fastball_idx = idx + 1
                    print(f"[{pid}] 직구 없음, 투심 사용")
                    break

        # 둘 다 없으면 None 처리
        if fastball_idx is None:
            print(f"[{pid}] 직구, 투심 모두 없음")
            results.append({'player_id': pid, 'speed': None})
            continue

        # 값 추출
        value_xpath = f'//*[@id="record_04"]/div/div/table/tbody/tr[1]/td[{fastball_idx}]'
        value = driver.find_element(By.XPATH, value_xpath).text.strip()
        value = value.split('k')[0]
        print(f"[{pid}] speed 수치: {value}")
        results.append({'player_id': pid, 'speed': value})

    except Exception as e:
        print(f"[{pid}] 오류 발생: {e}")
        results.append({'player_id': pid, 'speed': None})

driver.quit()

# 결과 병합 및 저장
speed_df = pd.DataFrame(results)
df_merged = pd.merge(df, speed_df, on='player_id', how='left')
df_merged.to_csv('data/all_pitcher_stats.csv', index=False)

print("✅ speed 컬럼 추가 및 저장 완료: data/all_pitcher_stats.csv")
