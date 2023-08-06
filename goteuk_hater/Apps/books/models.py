from django.db import models

# Create your models here.
class BookCategory(models.Model):
    id = models.IntegerField(primary_key=True)
    category = models.CharField(max_length=16)

class Book(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    written_by = models.CharField(max_length=128)
    publisher = models.CharField(max_length=128)
    category = models.IntegerField()
