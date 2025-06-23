source /mnt/c/Users/seong/KBO/uvenv/bin/activate
python /mnt/c/Users/seong/KBO/data/make_stat/00_hitters_stats.py

python /mnt/c/Users/seong/KBO/data/make_stat/01_pitchers_stats.py 
python /mnt/c/Users/seong/KBO/data/make_stat/02_get_velocity.py 
python /mnt/c/Users/seong/KBO/data/make_stat/03_preprocessing.py 
python /mnt/c/Users/seong/KBO/data/make_stat/04_player_style.py 
python /mnt/c/Users/seong/KBO/data/make_stat/05_kbo_schedule.py 
python /mnt/c/Users/seong/KBO/data/make_stat/07_hitters_daily_stat.py 
python /mnt/c/Users/seong/KBO/data/make_stat/08_pitchers_daliy_stat.py 
python /mnt/c/Users/seong/KBO/manage.py games
python /mnt/c/Users/seong/KBO/manage.py hitters
python /mnt/c/Users/seong/KBO/manage.py pitchers
python /mnt/c/Users/seong/KBO/manage.py daily_hitter_stat
python /mnt/c/Users/seong/KBO/manage.py daily_pitcher_stat