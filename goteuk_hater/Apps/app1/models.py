from django.db import models

# Create your models here.

class Student(models.Model):
    name = models.CharField(max_length=128)
    age = models.IntegerField()
    is_male = models.IntegerField()

    