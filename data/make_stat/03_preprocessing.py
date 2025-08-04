from stat_def import *

h_cols = [
    "team", "player_id", "player_name",
    "AVG", "G", "PA", "AB", "R", "H", "2B", "3B", "HR", "TB", "RBI", "SB", "CS", "SAC", "SF",
    "BB", "IBB", "HBP", "SO", "GDP", "SLG", "OBP", "E", "SB%", "MH", "OPS", "RISP", "PH-BA"
]
p_cols = [
    "team", "player_id", "player_name",
    "ERA", "G", "CG", "SHO", "W", "L", "SV", "HLD", "WPCT", "TBF", "NP", "IP", "H", "2B", "3B", "HR",
    "SAC", "SF", "BB", "IBB", "SO", "WP", "BK", "R", "ER", "BSV", "WHIP", "AVG", "QS"
]

# 문자열 컬럼이 아니면 그대로 반환
h_str_cols = ['player_name', 'team']
p_str_cols = ['player_name', 'team', 'IP']

# -를 0으로 대체하고 숫자형으로 변환
h_num_cols = num_cols(h_cols, h_str_cols)
p_num_cols = num_cols(p_cols, p_str_cols)

# 전처리 적용
h = preprocessing(h, h_num_cols)
p = preprocessing(p, p_num_cols)

# IP컬럼의 분수>float로 타입변경
p['IP'] = p['IP'].apply(parsing_0).round(3)

# 옛날 수식 h['power'] = ((h['HR']/h['PA']) * (0.6 + (h['SLG'] - h['AVG'])*0.2 + h['IBB']/h['PA']*0.2))
h['power'] = (h['HR']/h['HR'].max()/2 + 0.5).round(3)
h['contact'] = h['AVG']*0.45 + (1 - h['SO']/h['PA'])*0.2 + h['OBP']*0.2 + (1 - h['GDP']/h['PA'])*0.1 + h['PA']/h['PA'].max()*0.05
h['batting_eye'] = h['BB']/h['PA']*0.4 - h['SO']/h['PA']*0.2 + h['OBP']*0.4
h['speed'] = (h['SBA']/h['SBA'].max()/2 + 0.5).round(3)

p['stamina'] = p['NP']/p['IP']*0.4 + p['IP']/p['G']*0.4 + p['TBF']/p['IP']*0.2
# p['control'] = p['SO']/p['G']*0.5 + (1 - p['HBP']/p['G']*0.2) + (1 - p['H']/p['G']*0.3)
p['control'] = (p['SO'] / p['IP']) * 0.5 + (1 - p['BB'] / p['IP']) * 0.3 + (1 - p['H'] / p['IP']) * 0.2

p['fireball'] = (p['speed']/p['speed'].max()).round(3)

# 정규화된 스탯 적용
# 안씀 h['power'] = (normalize(game_count(h['power'], h['G'])) / 2 + 0.5).round(3) 안씀
h['contact'] = (normalize(game_count(h['contact'], h['G']))/2 + 0.5).round(3)
h['batting_eye'] = (normalize(game_count(h['batting_eye'], h['G']))/2 + 0.5).round(3)
# 안씀 h['speed'] = (normalize(game_count(h['speed'], h['G']))/2 + 0.5).round(3) 안씀

p['stamina'] = (normalize(game_count(p['stamina'], p['G']))/2 + 0.5).round(3)
p['control'] = (normalize(game_count(p['control'], p['G']))/2 + 0.5).round(3)

# CSV 저장
h.to_csv('data/all_hitter_stats.csv', index=False)
p.to_csv('data/all_pitcher_stats.csv', index=False)