from urllib.parse import quote

# 구글로 위경도 추출
def create_google_maps_direction_link(destination_lat, destination_lng):
    """
    목적지 좌표를 입력받아, 현위치에서 그곳까지의 Google Maps 경로 링크를 생성합니다.
    """
    base_url = "https://www.google.com/maps/dir/?api=1"
    # 'origin'을 생략하면 Google Maps가 사용자의 현재 위치를 기준으로 합니다.
    destination = f"{destination_lat},{destination_lng}"
    return f"{base_url}&destination={destination}&travelmode=driving"  # driving, walking, transit 등 선택 가능
# 예: 서울월드컵경기장 (월드컵로 240)의 좌표
stadium_lat = 37.568256
stadium_lng = 126.897240
link = create_google_maps_direction_link(stadium_lat, stadium_lng)

# 네이버지도

def create_naver_urls(team: str):
    """
    팀 코드를 입력받아 네이버 지도용 PC/모바일 URL을 생성합니다.
    WGS84 좌표(위도, 경도)를 기반으로 생성됩니다.
    """
    team_info = {
        'HT': '35.168275,126.888934,광주기아챔피언스필드,19909618',
        'OB': '37.512898,127.071107,잠실종합운동장잠실야구장,13202577',
        'LG': '37.512898,127.071107,잠실종합운동장잠실야구장,13202577',
        'SSG': '37.435123,126.693024,인천SSG 랜더스필드,13202558',
        'NC': '35.222571,128.582776,NC 다이노스,36046999',
        'HH': '36.317056,127.428072,(구 한화구장)한화생명이글스파크,11831114',
        'KW': '37.498184,126.867129,고척스카이돔,18967604',
        'LT': '35.194956,129.060426,부산사직종합운동장 사직야구장,13202715',
        'SS': '35.841965,128.681198,대구삼성라이온즈파크,19909612',
        'KT': '37.299025,126.974983,수원KT위즈파크,13491582'
    }

    code = team.strip().upper()
    if code not in team_info:
        raise ValueError(f"지원하지 않는 팀 코드: {team}")

    lat, lng, name, place_id = team_info[code].split(',', 3)

    pc_url = f"https://map.naver.com/p/directions/-/{lng},{lat},{quote(name)},{place_id}/PLACE_POI/-/car?c=15.00,0,0,0,dh"
    m_url = f"nmap://route/public?dlat={lat}&dlng={lng}&dname={quote(name)}"

    return pc_url, m_url

def show_team_list():
    teams = {
        'HT': '기아 타이거즈',
        'OB': '두산 베어스',
        'LG': 'LG 트윈스',
        'SSG': 'SSG 랜더스',
        'NC': 'NC 다이노스',
        'HH': '한화 이글스',
        'KW': '키움 히어로즈',
        'LT': '롯데 자이언츠',
        'SS': '삼성 라이온즈',
        'KT': 'KT 위즈'
    }
    print("사용 가능한 팀 코드:")
    for code, name in teams.items():
        print(f"{code}: {name}")

if __name__ == "__main__":
    print("KBO 야구장 네이버 지도 URL 생성기")
    print("------------------------------")
    show_team_list()
    print("\n팀 코드를 입력하세요 (예: KT, LG, SSG 등):")
    team_code = input(">>> ")

    try:
        pc_url, mobile_url = create_naver_urls(team_code)
        print("\n[결과]")
        print("1. 네이버맵 PC 웹 URL:")
        print(pc_url)
        print("\n2. 네이버맵 모바일 URL:")
        print(mobile_url)
    except ValueError as e:
        print(f"오류: {e}")
        print("올바른 팀 코드를 입력해주세요.")
