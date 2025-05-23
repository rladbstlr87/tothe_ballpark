import csv

with open('lineups.csv', 'r', encoding='utf-8-sig') as infile, \
     open('lineups_flatten.csv', 'w', newline='', encoding='utf-8-sig') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.writer(outfile)
    writer.writerow(['date', 'time', 'team1', 'team2', 'team1_player', 'team2_player'])

    for row in reader:
        team1_players = [x.strip() for x in row['team1_lineup'].split(',') if x.strip()]
        team2_players = [x.strip() for x in row['team2_lineup'].split(',') if x.strip()]
        max_len = max(len(team1_players), len(team2_players))
        # 빈칸으로 맞추기
        team1_players += [''] * (max_len - len(team1_players))
        team2_players += [''] * (max_len - len(team2_players))
        for p1, p2 in zip(team1_players, team2_players):
            writer.writerow([row['date'], row['time'], row['team1'], row['team2'], p1, p2])