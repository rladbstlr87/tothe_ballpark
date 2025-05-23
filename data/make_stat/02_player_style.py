from stat_def import *

if (h['HR']/h['HR'].max()) > 0.4:
    h['style'] = 0 # 홈런 타입
elif (h['SBA']/h['SBA'].max()) > 0.4:
    h['style'] = 1 # 스피드 타입
else:
    h['style'] = 2 # 컨택 타입

if (p['velocity']/p['velocity'].avg()) > 0.7:
    p['style'] = 0 # 파이어볼러 타입
elif p['SO']/p['G']*0.5 + (1 - p['HBP']/p['G']*0.2) + (1 - p['H']/p['G']*0.3) > 0.4:
    p['style'] = 1 # 제구력 타입
else:
    p['style'] = 2 # 무쇠팔 타입

h.to_csv('../data/all_hitter_stats.csv', index=False)
p.to_csv('../data/all_pitcher_stats.csv', index=False)