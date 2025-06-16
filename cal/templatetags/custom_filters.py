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

@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key))

@register.filter
def style_description(obj):
    style_value = str(getattr(obj, 'style', ''))
    is_pitcher = hasattr(obj, 'ERA') or hasattr(obj, 'IP')  # 투수만 가질 만한 필드

    if is_pitcher:
        pitcher_styles = {
            '0': '구속형',
            '1': '제구형',
            '2': '체력형',
            '3': '노멀형',
        }
        return pitcher_styles.get(style_value, '알 수 없는 유형')
    else:
        hitter_styles = {
            '0': '파워형',
            '1': '스피드형',
            '2': '타격형',
            '3': '선구안형',
            '4': '노멀형',
        }
        return hitter_styles.get(style_value, '알 수 없는 유형')
