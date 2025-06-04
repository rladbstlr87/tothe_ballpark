from django import template

register = template.Library()

@register.filter
def percent(value):
    try:
        return round(float(value) * 100)
    except (ValueError, TypeError):
        return ''
    
@register.filter
def speed_percent(value):
    try:
        value = float(value)
        min_speed = 105
        max_speed = 156
        normalized = (value - min_speed) / (max_speed - min_speed)
        # 0~1 사이로 제한 (클램핑)
        clamped = max(0, min(1, normalized))
        return round(clamped * 100)
    except (ValueError, TypeError):
        return ''
    
TEAM_MAP = {
    "HH": "한화",
    "LT": "롯데",
    "LG": "LG",
    "OB": "두산",
    "KT": "KT",
    "WO": "키움",
    "NC": "NC",
    "HT": "KIA",
    "SK": "SSG",
    "SS": "삼성"
}
@register.filter
def team_name(code):
    return TEAM_MAP.get(code, code)