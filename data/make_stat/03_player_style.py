from stat_def import *

h['style'] = h.apply(hitter_style, axis=1)
p['style'] = p.apply(pitcher_style, axis=1)

h.to_csv('../all_hitter_stats.csv', index=False)
p.to_csv('../all_pitcher_stats.csv', index=False)

# print((h['style'] == 0).sum())
# print((h['style'] == 1).sum())
# print((h['style'] == 2).sum())
# print((h['style'] == 3).sum())
# print('')
# print((p['style'] == 0).sum())
# print((p['style'] == 1).sum())
# print((p['style'] == 2).sum())
# print((p['style'] == 3).sum())

# print(h.loc[h['style'] == 2, '선수명'].to_list())
# print(p.loc[p['style'] == 0, '선수명'].to_list())
