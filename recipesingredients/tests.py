from django.test import TestCase
from django.contrib.auth.models import User
from recipes.models import Recipe
from ingredients.models import Ingredient
from recipesingredients.models import RecipeIngredient


class RecipeIngredientModelTest(TestCase):
    def setUp(self):
        """ set the test data """
        self.user = User.objects.create_user(
            username="testuser", password="testpass")
        self.recipe = Recipe.objects.create(
            name="Test Recipe",
            cooking_time=30,
            ingredient_num=0,  # no ingredient when init
            created_by=self.user
        )
        self.ingredient1 = Ingredient.objects.create(name="Tomato")
        self.ingredient2 = Ingredient.objects.create(name="Salt")

    def test_recipe_ingredient_creation_updates_ingredient_num(self):
        """ test ingredient_num will update or not when RecipeIngredient update"""
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.ingredient1, quantity="2 cups")
        self.recipe.refresh_from_db()  # reload the database
        self.assertEqual(self.recipe.ingredient_num, 1)

        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.ingredient2, quantity="1 tsp")
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.ingredient_num, 2)

    def test_recipe_ingredient_deletion_updates_ingredient_num(self):
        """ test ingredient_num will decrease or not when RecipeIngredient update """
        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.ingredient1, quantity="2 cups"
        )
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.ingredient_num, 1)

        recipe_ingredient.delete()  # delete ingredients
        self.recipe.refresh_from_db()
        # ingredient_num should back to 0
        self.assertEqual(self.recipe.ingredient_num, 0)
