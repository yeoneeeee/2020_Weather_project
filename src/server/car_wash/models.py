from django.db import models

# Create your models here.
from django.utils import timezone


class Washer(models.Model):
    name = models.CharField(max_length=10)
    lat = models.FloatField()
    lon = models.FloatField()

    def __str__(self):
        return self.name
