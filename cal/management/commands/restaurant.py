import csv
from django.core.management.base import BaseCommand
from cal.models import Restaurant, Stadium
from django.conf import settings

class Command(BaseCommand):
    help = 'CSV 파일로부터 맛집 데이터를 Restaurant 테이블에 저장함'

    def handle(self, *args, **kwargs):
        file_path = settings.BASE_DIR / 'data' / 'restaurant.csv'

        with open(file_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            total, created_count, skipped = 0, 0, 0

            for row in reader:
                total += 1
                stadium_name = row['stadium'].strip()
                restaurant_name = row['restaurant_name'].strip()
                adress = row['address'].strip()
                note = row['note'].strip()

                try:
                    stadium_obj = Stadium.objects.get(stadium=stadium_name)
                except Stadium.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"❗ stadium '{stadium_name}' not found. Skipping {restaurant_name}"))
                    skipped += 1
                    continue

                obj, created = Restaurant.objects.update_or_create(
                    stadium=stadium_obj,
                    restaurant_name=restaurant_name,
                    defaults={
                        'adress': adress,
                        'note': note[:200],
                    }
                )

                if created:
                    created_count += 1

            self.stdout.write(self.style.SUCCESS(f"🍽️ {created_count}개 식당 추가 완료 / {skipped}개 누락 / 총 {total}건 처리 완료"))
