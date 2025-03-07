from django.db import models
from recipes.models import Recipe
from ingredients.models import Ingredient


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="unique_recipe_ingredient"
            )
        ]

    def save(self, *args, **kwargs):

        ingredient, created = Ingredient.objects.get_or_create(
            name=self.ingredient.name)
        self.ingredient = ingredient

        """ change recipe.ingredient_num when add/update """
        super().save(*args, **kwargs)

        self.recipe.ingredient_num = RecipeIngredient.objects.filter(
            recipe=self.recipe).count()
        self.recipe.save()

    def delete(self, *args, **kwargs):
        """ change recipe.ingredient_num when delete """
        super().delete(*args, **kwargs)
        self.recipe.ingredient_num = RecipeIngredient.objects.filter(
            recipe=self.recipe).count()
        self.recipe.save()

    def __str__(self):
        return f"{self.quantity} of {self.ingredient.name} in {self.recipe.name}"
