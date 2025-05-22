from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import csv

driver = webdriver.Chrome()
URL = 'https://statiz.sporki.com/'
driver.get(URL)

players = ['문동주', '김현수', '류현진', '양현종']

# csv 파일 저장
filename = 'pitching_speed.csv'

with open(filename, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['팀명', '선수명', '구속', '생년'])  # 헤더

    # 반복 시작했다
    for player in players:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.btn_box')))
        finder = driver.find_element(By.CSS_SELECTOR, 'a.btn_box')
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.btn_box')))
        finder.click()

        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 's')))
        input_box = driver.find_element(By.ID, 's')
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 's')))
        input_box.click()
        input_box.clear()

        # player = '문동주'
        input_box.send_keys(player)
        time.sleep(1)
        input_box.send_keys(Keys.RETURN)


        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.table_type01 > table > tbody > tr > td')))
        tbody_elements = driver.find_elements(By.CSS_SELECTOR, 'div.table_type01 > table > tbody')

        if tbody_elements:
            is_pitcher = driver.find_element(By.CSS_SELECTOR, 'div.table_type01 > table > tbody > tr:nth-child(1) > td:nth-child(7)').text
            if is_pitcher == 'P':
                pitcher_name = driver.find_element(By.CSS_SELECTOR, 'div.table_type01 > table > tbody > tr:nth-child(1) > td:nth-child(1) > a')
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.table_type01 > table > tbody > tr:nth-child(1) > td:nth-child(1) > a')))
                pitcher_name.click()

            else:
                pitcher_name = driver.find_element(By.CSS_SELECTOR, 'div.table_type01 > table > tbody > tr:nth-child(2) > td:nth-child(1) > a')
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.table_type01 > table > tbody > tr:nth-child(2) > td:nth-child(1) > a')))
                pitcher_name.click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'name')))
        # print(팀명)
        team_span = driver.find_element(By.CSS_SELECTOR, 'div.con > span:first-of-type').text
        # print(team_span)

        # print(선수명)
        speed = ''
        try:
            # 14번째 'item' 요소가 로드될 때까지 (최대 10초)
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.CLASS_NAME, 'item')) >= 14
            )

            # tooltip span이 하나라도 나올 때까지 (최대 10초)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.rang_info > span'))
            )

            target_item = driver.find_elements(By.CLASS_NAME, 'item')
            for div in target_item:
                # span 태그 없으면 건너뛰기
                try:
                    label = div.find_element(By.TAG_NAME, 'span').text
                except NoSuchElementException:
                    continue

                if '직구평균구속' not in label:
                    continue

                # tooltip 속성에서 숫자 추출
                try:
                    tooltip = div.find_element(
                        By.CSS_SELECTOR, 'div.rang_info > span'
                    ).get_attribute('tooltip')
                    parts = tooltip.split()
                    raw = parts[1] if '위' in tooltip else parts[0]
                    speed = round(float(raw), 1)
                except (NoSuchElementException, ValueError):
                    speed = ''
                break

        except TimeoutException:
            # 요소가 너무 늦게 뜨거나 없으면 speed='' 상태 유지
            pass

        print(f"직구평균구속: {speed}")
        # print(생년)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.man_info > li:first-of-type')))
        birth = driver.find_element(By.CSS_SELECTOR, 'ul.man_info > li:first-of-type').text.split(':', 1)[1].strip()
        birth = birth.replace('년 ', '-').replace('월 ', '-').replace('일', '')
        # print(birth)

    # 반복끝났다

        writer.writerow([team_span, player, speed, birth])