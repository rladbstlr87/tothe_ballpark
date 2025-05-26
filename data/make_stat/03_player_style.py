from stat_def import *

h['style'] = h.apply(hitter_style, axis=1)
p['style'] = p.apply(pitcher_style, axis=1)

h.to_csv('../all_hitter_stats.csv', index=False)
p.to_csv('../all_pitcher_stats.csv', index=False)