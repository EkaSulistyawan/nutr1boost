from django.db import models

# Create your models here.
class Menu(models.Model):
    meal_name       = models.CharField(max_length=255)
    ja_meal_name    = models.CharField(max_length=255,null=True)
    meal_type       = models.CharField(max_length=255)
    description     = models.CharField(max_length=255,null=True)
    img_name        = models.CharField(max_length=255,null=True)
    showmeal        = models.BooleanField(default=False,null=True)
    price           = models.IntegerField()
    energy          = models.FloatField()
    protein         = models.FloatField()
    fat             = models.FloatField()
    carbohydrate    = models.FloatField()
    fiber           = models.FloatField()
    calcium         = models.FloatField()
    veggies         = models.FloatField()

    def __str__(self):
        return f'{self.meal_name}'
