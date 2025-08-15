# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import TypedDict, Dict, List, Optional
from urllib.parse import quote

# =============================
# JSON 스타일 설정 스키마 (TypedDict)
# =============================
class TeamConfRequired(TypedDict):
    name_ko: str
    name_en: str
    home_stadiums: List[str]

class TeamConf(TeamConfRequired, total=False):
    ticket_url: str
    days_before: int
    colors: Dict[str, str]

class StadiumConfRequired(TypedDict):
    name: str
    lat: str
    lng: str
    place_id: str

class StadiumConf(StadiumConfRequired, total=False):
    ticket_url: str
    days_before: int

# =============================
# 별칭(선택)
# =============================
TEAM_ALIASES: Dict[str, str] = {
    # 예: "DO": "OB"
}

STADIUM_ALIASES: Dict[str, str] = {
    # 예: "인천": "문학", "인천SSG": "문학"
}

# =============================
# 팀: 최상위 키가 팀 코드
# =============================
TEAMS: Dict[str, TeamConf] = {
    "LG": {
        "name_ko": "LG 트윈스",
        "name_en": "LG Twins",
        "home_stadiums": ["잠실"],
        "days_before": 7,
        "colors": {"primary": "#A50034", "accent": "#000000"},
    },
    "OB": {
        "name_ko": "두산 베어스",
        "name_en": "Doosan Bears",
        "home_stadiums": ["잠실"],
        "days_before": 7,
        "colors": {"primary": "#1A1748"},
    },
    "SS": {
        "name_ko": "삼성 라이온즈",
        "name_en": "Samsung Lions",
        "home_stadiums": ["대구", "포항"],
        "ticket_url": "https://www.ticketlink.co.kr/sports/137/57",
        "days_before": 7,
        "colors": {"primary": "#074CA1"},
    },
    "HH": {
        "name_ko": "한화 이글스",
        "name_en": "Hanwha Eagles",
        "home_stadiums": ["대전"],
        "ticket_url": "https://www.ticketlink.co.kr/sports/137/63",
        "days_before": 7,
        "colors": {"primary": "#FC4E00"},
    },
    "HT": {
        "name_ko": "KIA 타이거즈",
        "name_en": "KIA Tigers",
        "home_stadiums": ["광주"],
        "ticket_url": "https://www.ticketlink.co.kr/sports/137/58",
        "days_before": 7,
        "colors": {"primary": "#EA0029"},
    },
    "LT": {
        "name_ko": "롯데 자이언츠",
        "name_en": "Lotte Giants",
        "home_stadiums": ["사직"],
        "ticket_url": "https://ticket.giantsclub.com/loginForm.do",
        "days_before": 7,
        "colors": {"primary": "#041E42", "accent": "#CE0E2D"},
    },
    "NC": {
        "name_ko": "NC 다이노스",
        "name_en": "NC Dinos",
        "home_stadiums": ["창원", "울산"],
        "ticket_url": "https://ticket.ncdinos.com/games",
        "days_before": 6,
        "colors": {"primary": "#1D467C"},
    },
    "KT": {
        "name_ko": "KT 위즈",
        "name_en": "KT Wiz",
        "home_stadiums": ["수원"],
        "ticket_url": "https://www.ticketlink.co.kr/sports/137/62",
        "days_before": 7,
        "colors": {"primary": "#000000"},
    },
    "SK": {
        "name_ko": "SSG 랜더스",
        "name_en": "SSG Landers",
        "home_stadiums": ["문학"],
        "ticket_url": "https://www.ticketlink.co.kr/sports/137/476",
        "days_before": 4,
        "colors": {"primary": "#CE0E2D", "accent": "#B9975B"},
    },
    "WO": {
        "name_ko": "키움 히어로즈",
        "name_en": "Kiwoom Heroes",
        "home_stadiums": ["고척"],
        "ticket_url": "https://ticket.interpark.com/Contents/Sports/GoodsInfo?SportsCode=07001&TeamCode=PB003",
        "days_before": 7,
        "colors": {"primary": "#5E0F15"},
    },
}

# =============================
# 구장: 키는 표준화된 구장명 ("사직", "잠실" 등)
# =============================
STADIUMS: Dict[str, StadiumConf] = {
    "광주": {"name": "광주기아챔피언스필드", "lat": "35.168275", "lng": "126.888934", "place_id": "19909618", "ticket_url": "https://www.ticketlink.co.kr/sports/137/58"},
    "잠실": {"name": "잠실종합운동장 잠실야구장", "lat": "37.512898", "lng": "127.071107", "place_id": "13202577"},
    "문학": {"name": "인천SSG 랜더스필드", "lat": "37.435123", "lng": "126.693024", "place_id": "13202558", "ticket_url": "https://www.ticketlink.co.kr/sports/137/476"},
    "창원": {"name": "NC 다이노스", "lat": "35.222571", "lng": "128.582776", "place_id": "36046999", "ticket_url": "https://ticket.ncdinos.com/games"},
    "대전": {"name": "한화생명이글스파크", "lat": "36.317056", "lng": "127.428072", "place_id": "11831114", "ticket_url": "https://www.ticketlink.co.kr/sports/137/63"},
    "고척": {"name": "고척스카이돔", "lat": "37.498184", "lng": "126.867129", "place_id": "18967604", "ticket_url": "https://ticket.interpark.com/Contents/Sports/GoodsInfo?SportsCode=07001&TeamCode=PB003"},
    "사직": {"name": "부산사직종합운동장 사직야구장", "lat": "35.194956", "lng": "129.060426", "place_id": "13202715", "ticket_url": "https://ticket.giantsclub.com/loginForm.do"},
    "대구": {"name": "대구삼성라이온즈파크", "lat": "35.841965", "lng": "128.681198", "place_id": "19909612", "ticket_url": "https://www.ticketlink.co.kr/sports/137/57"},
    "수원": {"name": "수원KT위즈파크", "lat": "37.299025", "lng": "126.974983", "place_id": "13491582", "ticket_url": "https://www.ticketlink.co.kr/sports/137/62"},
    "울산": {"name": "울산문수야구장", "lat": "35.532168", "lng": "129.265575", "place_id": "1406092164", "ticket_url": "https://ticket.ncdinos.com/games"},
    "포항": {"name": "포항야구장", "lat": "36.0081953", "lng": "129.3593993", "place_id": "11830535", "ticket_url": "https://www.ticketlink.co.kr/sports/137/57"},
}

# =============================
# 정규화 & 유틸 함수
# =============================

def normalize_team_code(code: Optional[str]) -> Optional[str]:
    if not code:
        return None
    c = code.strip().upper()
    return TEAM_ALIASES.get(c, c)


def normalize_stadium_key(key: Optional[str]) -> Optional[str]:
    if not key:
        return None
    k = key.strip()
    return STADIUM_ALIASES.get(k, k)


def build_map_urls(stadium_key: str) -> tuple[str, str]:
    k = normalize_stadium_key(stadium_key)
    s = STADIUMS.get(k or "")
    if not s:
        return "#", "#"
    google = f"https://www.google.com/maps/dir/?api=1&destination={s['lat']},{s['lng']}&destination_place_id={s['place_id']}"
    naver = f"nmap://route/public?dlat={s['lat']}&dlng={s['lng']}&dname={quote(s['name'])}"
    return google, naver


def resolve_ticket_url(team_code: Optional[str], stadium_key: Optional[str]) -> str:
    c = normalize_team_code(team_code)
    if c and (team := TEAMS.get(c)) and ('ticket_url' in team):
        return team['ticket_url']
    k = normalize_stadium_key(stadium_key)
    if k and (st := STADIUMS.get(k)) and ('ticket_url' in st):
        return st['ticket_url']
    return "#"


def get_days_before(team_code: Optional[str], stadium_key: Optional[str] = None, default: int = 7) -> int:
    """팀 우선 → (선택) 구장 → 기본값 순으로 일자 반환."""
    c = normalize_team_code(team_code)
    if c and (team := TEAMS.get(c)):
        v = team.get('days_before')
        if isinstance(v, int):
            return v
    k = normalize_stadium_key(stadium_key) if stadium_key else None
    if k and (st := STADIUMS.get(k)):
        v2 = st.get('days_before')
        if isinstance(v2, int):
            return v2
    return default


def is_home(team_code: Optional[str], stadium_key: Optional[str]) -> bool:
    c = normalize_team_code(team_code)
    k = normalize_stadium_key(stadium_key)
    if not c or not k:
        return False
    team = TEAMS.get(c)
    return bool(team and k in team.get('home_stadiums', []))


def home_flags(team1_code: str, team2_code: str, stadium_key: str) -> tuple[bool, bool]:
    t1 = is_home(team1_code, stadium_key)
    t2 = is_home(team2_code, stadium_key)
    # 잠실 공동 사용: 기존 동작 유지(둘 다 잠실 홈이면 team2를 홈으로)
    if normalize_stadium_key(stadium_key) == "잠실" and t1 and t2:
        return False, True
    return t1, t2


__all__ = [
    # 스키마
    "TeamConfRequired", "TeamConf", "StadiumConfRequired", "StadiumConf",
    # 데이터
    "TEAMS", "STADIUMS", "TEAM_ALIASES", "STADIUM_ALIASES",
    # 유틸
    "normalize_team_code", "normalize_stadium_key", "build_map_urls",
    "resolve_ticket_url", "get_days_before", "is_home", "home_flags",
]
