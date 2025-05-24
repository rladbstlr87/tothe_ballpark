import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

driver = webdriver.Chrome()
driver.get("https://m.sports.naver.com/player/index?from=sports&category=kbo&playerId=63950&tab=record")

# all_pitcher_stats.csv 읽기
df = pd.read_csv('../all_pitcher_stats.csv')
df['선수명'] = df['선수명'].astype(str)
df['팀명'] = df['팀명'].astype(str)

# velocity 데이터를 저장할 리스트
velocity_data = []

print(f"총 {len(df)} 명의 투수 데이터 수집 시작")

for idx, row in df.iterrows():
    player_name = row['선수명']
    team_name = row['팀명']
    player_id = row.get('선수ID', idx)  # 선수ID 컬럼이 있다면 사용, 없으면 인덱스 사용
    
    print(f"\n▶ [{idx+1}/{len(df)}] {player_name}({team_name}) 검색 중...")
    
    try:
        # 검색창 찾기 및 기존 텍스트 삭제
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "end_search_input"))
        )
        search_input.clear()
        time.sleep(0.5)
        
        # 선수명 입력
        search_input.send_keys(player_name)
        time.sleep(1.5)  # 드롭다운이 나타날 시간 대기
        
        # 드롭다운에서 해당 팀 선수 찾기
        dropdown_found = False
        try:
            # 드롭다운 옵션들 찾기
            dropdown_options = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".search_team_name"))
            )
            
            for option in dropdown_options:
                if option.text.strip() == team_name:
                    option.click()
                    dropdown_found = True
                    print(f"  ✔ {team_name} 팀 {player_name} 선택됨")
                    break
            
        except Exception as e:
            print(f"  ⚠ 드롭다운에서 {team_name} 팀 {player_name}를 찾을 수 없음: {e}")
        
        if dropdown_found:
            # 페이지 로딩 대기
            time.sleep(2)
            
            try:
                # velocity 요소 찾기
                velocity_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#record_04 > div > div > table > tbody > tr.line > td:nth-child(1)"))
                )
                velocity_value = velocity_element.text.strip()
                
                velocity_data.append({
                    '선수ID': player_id,
                    '선수명': player_name,
                    '팀명': team_name,
                    'velocity': velocity_value
                })
                
                print(f"  ✔ velocity: {velocity_value}")
                
            except Exception as e:
                print(f"  ⚠ velocity 데이터 추출 실패: {e}")
                velocity_data.append({
                    '선수ID': player_id,
                    '선수명': player_name,
                    '팀명': team_name,
                    'velocity': None
                })
        else:
            print(f"  ⚠ {team_name} 팀 {player_name} 선수를 찾을 수 없음")
            velocity_data.append({
                '선수ID': player_id,
                '선수명': player_name,
                '팀명': team_name,
                'velocity': None
            })
    
    except Exception as e:
        print(f"  ❌ {player_name} 처리 중 오류 발생: {e}")
        velocity_data.append({
            '선수ID': player_id,
            '선수명': player_name,
            '팀명': team_name,
            'velocity': None
        })
    
    # 요청 간 딜레이
    time.sleep(1)

# velocity 데이터프레임 생성
if velocity_data:
    df_velocity = pd.DataFrame(velocity_data)
    print(f"\n✔ velocity 데이터 수집 완료 - 총 {len(df_velocity)}건")
    
    # 기존 velocity 컬럼이 있다면 제거
    if 'velocity' in df.columns:
        df = df.drop(columns=['velocity'])
        print("기존 velocity 컬럼 제거")
    
    # 선수ID를 기준으로 병합
    df_merged = pd.merge(
        df, 
        df_velocity[['선수ID', 'velocity']], 
        on='선수ID', 
        how='left'
    )
    
    print(f"\n✔ df과 병합 완료 - 최종 데이터: {len(df_merged)}행")
    df_merged.to_csv("../all_pitcher_stats.csv", index=False, encoding='utf-8-sig')
    
    # 수집 결과 요약
    successful_count = df_velocity['velocity'].notna().sum()
    failed_count = df_velocity['velocity'].isna().sum()
    print(f"\n📊 수집 결과:")
    print(f"  - 성공: {successful_count}건")
    print(f"  - 실패/누락: {failed_count}건")
    
else:
    print("\n⚠ 수집된 velocity 데이터가 없습니다")
    df_merged = df