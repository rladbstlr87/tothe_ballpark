from django.db import models

# Create your models here.

class Game(models.Model):
    date = models.DateField()
    time = models.TimeField()
    away_team = models.CharField(max_length = 100)
    home_team = models.CharField(max_length = 100)
    stadium = models.CharField(max_length = 100)
    play = models.CharField(max_length=100, null=True, blank=True)
    note = models.CharField(max_length=100, null=True, blank=True)
    result = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return f"{self.away_team} vs {self.away_team} on {self.date}"
    
    