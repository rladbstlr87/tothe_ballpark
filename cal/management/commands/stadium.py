from django.core.management.base import BaseCommand
from cal.models import Stadium
from django.conf import settings
import pandas as pd

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        csv_file_path = settings.BASE_DIR / 'data' / 'kbo_schedule.csv'
        try:
            df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
            stadium_names = df['stadium'].unique()

            count = 0
            for name in stadium_names:
                if pd.notna(name) and name:
                    obj, created = Stadium.objects.get_or_create(stadium=name)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created: {name}'))
                    else:
                        self.stdout.write(f'Exists: {name}')
                    count += 1

            self.stdout.write(self.style.SUCCESS(f"{count} stadium(s) processed."))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"CSV file not found at {csv_file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
