from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse


class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Intermediate', 'Intermediate'),
        ('Hard', 'Hard'),
    ]

    name = models.CharField(max_length=255, db_index=True)
    cooking_time = models.PositiveIntegerField(
        help_text="Cooking time in minutes")
    ingredient_num = models.PositiveIntegerField(default=0)
    difficulty = models.CharField(
        max_length=15, choices=DIFFICULTY_CHOICES, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    pic = models.ImageField(upload_to='recipes', default='no_picture.jpg')

    def __str__(self):
        return self.name

    @property
    def calculate_difficulty(self):
        if self.cooking_time < 10 and self.ingredient_num < 4:
            return "Easy"
        elif self.cooking_time < 10 and self.ingredient_num >= 4:
            return "Medium"
        elif self.cooking_time >= 10 and self.ingredient_num < 4:
            return "Intermediate"
        return "Hard"

    def save(self, *args, **kwargs):
        """ update difficulty before save """
        self.difficulty = self.calculate_difficulty  # update difficulty automatically
        super().save(*args, **kwargs)  # call save() and save data

    def get_absolute_url(self):
        return reverse('recipes:recipe_detail', kwargs={'pk': self.pk})
