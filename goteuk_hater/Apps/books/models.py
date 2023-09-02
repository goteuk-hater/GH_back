from django.db import models

# Create your models here.
class BookCategory(models.Model):
    id = models.IntegerField(primary_key=True)
    category = models.CharField(max_length=16)

class Book(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=128)
    author = models.CharField(max_length=128)
    publisher = models.CharField(max_length=128)
    image_url = models.CharField(max_length=256, null=True)
    category = models.ForeignKey("BookCategory", related_name="BookCategory",
                                 on_delete=models.CASCADE, db_column='category')
