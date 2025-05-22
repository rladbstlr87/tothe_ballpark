from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import datetime

# today = datetime.today().strftime('%Y%m%d')  # 오늘 날짜 (예: '20250516')
today = '20250515'  # 테스트용 날짜
our_team_code = 'LT'   # 예: 롯데
opponent_team_code = 'HT'  # 예: KIA
game_id = '02025'  # 경기 고유번호

# ✅ URL 구성
url = f'https://m.sports.naver.com/game/{today}{our_team_code}{opponent_team_code}{game_id}/lineup'

driver = webdriver.Chrome()
driver.get(url)

time.sleep(3)

lineup_boxes = driver.find_elements(By.CSS_SELECTOR, 'div.Lineup_comp_lineup__361i1 > div > div')

our_team = []
opponent_team = []

for idx, team_box in enumerate(lineup_boxes[:2]):
    players = team_box.find_elements(By.CSS_SELECTOR, 'ol > li > a > div > strong')
    player_names = [player.text for player in players]
    
    if idx == 0:
        our_team = player_names
    else:
        opponent_team = player_names

# ✅ 출력
print("✅ 우리 팀 라인업:")
for name in our_team:
    print("-", name)

print("\n✅ 상대 팀 라인업:")
for name in opponent_team:
    print("-", name)

# ✅ 브라우저 종료
driver.quit()
