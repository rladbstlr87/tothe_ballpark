from django.db import models

# Create your models here.

class Game(models.Model):
    date = models.DateField()
    time = models.TimeField()
    team1 = models.CharField(max_length = 100)
    team2 = models.CharField(max_length = 100)
    team1_score = models.IntegerField(null=True, blank=True)
    team2_score = models.IntegerField(null=True, blank=True)
    team1_result = models.CharField(max_length = 100)
    team2_result = models.CharField(max_length = 100)
    stadium = models.CharField(max_length = 100)
    note = models.CharField(max_length=100, null=True, blank=True)