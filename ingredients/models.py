from django.db import models
from django.shortcuts import reverse


class Ingredient(models.Model):
    name = models.CharField(max_length=120, unique=True,
                            db_index=True)
    introduction = models.TextField(blank=True, null=True)
    pic = models.ImageField(upload_to='ingredients', default='no_picture.jpg')

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
       return reverse ('ingredients:ingredient-detail', kwargs={'pk': self.pk})
