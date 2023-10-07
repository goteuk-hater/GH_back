from django.db import models

# Create your models here.
class Division(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()

class Inquiry(models.Model):
    title = models.TextField()
    content = models.TextField()
    division = models.ForeignKey("Division", related_name="Division",
                                 on_delete=models.CASCADE, db_column='name')