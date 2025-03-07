from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from recipes.models import Recipe
from recipesingredients.models import RecipeIngredient
from ingredients.models import Ingredient

from recipes.forms import RecipeForm, RecipeIngredientForm, IngredientSearchForm


class RecipeModelTest(TestCase):
    def setUp(self):
        """Create test user and a sample recipe."""
        self.user = User.objects.create_user(
            username="testuser", password="testpass")
        self.recipe = Recipe.objects.create(
            name="Test Recipe",
            cooking_time=20,
            ingredient_num=2,
            created_by=self.user
        )
        self.ingredient1 = Ingredient.objects.create(name="Salt")
        self.ingredient2 = Ingredient.objects.create(name="Pepper")

        # Create RecipeIngredient relations
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.ingredient1, quantity="1 tsp")
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.ingredient2, quantity="1/2 tsp")

    def test_recipe_creation(self):
        """Test if the Recipe instance is created correctly."""
        self.assertEqual(self.recipe.name, "Test Recipe")
        self.assertEqual(self.recipe.calculate_difficulty, "Intermediate")

    def test_recipe_ingredient_relation(self):
        """Test if Recipe correctly associates with RecipeIngredient."""
        self.assertEqual(self.recipe.recipeingredient_set.count(), 2)

    def test_get_absolute_url(self):
        """Test if get_absolute_url() returns the correct URL."""
        expected_url = reverse('recipes:recipe_detail',
                               kwargs={'pk': self.recipe.pk})
        self.assertEqual(self.recipe.get_absolute_url(), expected_url)


class RecipeFormTest(TestCase):
    def test_recipe_form_valid(self):
        """Test if RecipeForm validates correctly with valid data."""
        form_data = {
            "name": "Pancakes",
            "cooking_time": 15,
            "ingredient_num": 3
        }
        form = RecipeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_recipe_ingredient_form_valid(self):
        """Test if RecipeIngredientForm handles input correctly."""
        ingredient = Ingredient.objects.create(name="Milk")
        form_data = {
            "ingredient": ingredient.id,  # input ID
            "quantity": "1 cup"
        }
        form = RecipeIngredientForm(data=form_data)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_ingredient_search_form_valid(self):
        """Test if IngredientSearchForm validates correctly."""
        form = IngredientSearchForm(data={"ingredient": "Flour"})
        self.assertTrue(form.is_valid())

    def test_ingredient_search_form_empty(self):
        """Test if IngredientSearchForm allows empty input."""
        form = IngredientSearchForm(data={"ingredient": ""})
        self.assertTrue(form.is_valid())


class RecipeViewsTest(TestCase):
    def setUp(self):
        """Create a test user, ingredients, and recipes."""
        self.user = User.objects.create_user(
            username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        # Create ingredients
        self.ingredient1 = Ingredient.objects.create(name="Onion")
        self.ingredient2 = Ingredient.objects.create(name="Milk")

        # Create recipes
        self.recipe1 = Recipe.objects.create(
            name="Onion Soup", cooking_time=30, ingredient_num=2, created_by=self.user)
        self.recipe2 = Recipe.objects.create(
            name="Milkshake", cooking_time=10, ingredient_num=1, created_by=self.user)

        # Link recipes to ingredients
        RecipeIngredient.objects.create(
            recipe=self.recipe1, ingredient=self.ingredient1, quantity="1")
        RecipeIngredient.objects.create(
            recipe=self.recipe2, ingredient=self.ingredient2, quantity="1 cup")

    def test_recipe_create_view(self):
        """Test if RecipeCreateView correctly creates a new recipe."""
        response = self.client.post(reverse("recipes:recipe_create"), {
            "name": "Omelette",
            "cooking_time": 10,
            "ingredient_num": 2
        })
        # Should redirect after success
        self.assertEqual(response.status_code, 302)
        # Ensure new recipe is created
        self.assertEqual(Recipe.objects.count(), 3)

    def test_add_ingredient_view(self):
        """Test if RecipeIngredientCreateView allows adding ingredients."""
        recipe = Recipe.objects.create(
            name="Omelette", cooking_time=10, ingredient_num=2, created_by=self.user)

        egg = Ingredient.objects.create(name="Egg")
        cheese = Ingredient.objects.create(name="Cheese")

        response = self.client.post(reverse("recipes:recipe_add_ingredients", args=[recipe.id]), {
            "form-0-ingredient": egg.id,  # ID
            "form-0-quantity": "2",
            "form-1-ingredient": cheese.id,  # ID
            "form-1-quantity": "1 slice",
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
        })
        self.assertEqual(response.status_code, 302,
                         msg=response.content)  # print debug
        self.assertEqual(RecipeIngredient.objects.filter(
            recipe=recipe).count(), 2)

    def test_ingredient_search_view(self):
        """Test if the ingredient search page loads correctly."""
        response = self.client.get(reverse('recipes:ingredient_search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/ingredient_search.html')

    def test_pie_chart_generation(self):
        """Test if Pie Chart generates correctly when an ingredient is provided."""
        response = self.client.get(reverse('recipes:ingredient_search'), {
                                   'ingredient': 'Onion', 'chart_type': '#1'})
        self.assertIsNotNone(response.context.get("chart"))

    def test_bar_chart_generation(self):
        """Test if Bar Chart generates correctly."""
        response = self.client.get(
            reverse('recipes:ingredient_search'), {'chart': '#2'})
        self.assertIsNotNone(response.context.get("chart"))

    def test_line_chart_generation(self):
        """Test if Line Chart generates correctly."""
        response = self.client.get(
            reverse('recipes:ingredient_search'), {'chart': '#3'})
        self.assertIsNotNone(response.context.get("chart"))

    def test_unauthorized_access(self):
        """Test if an unauthorized user is redirected to login page."""
        self.client.logout()
        response = self.client.get(reverse('recipes:ingredient_search'))
        # Should redirect to login
        self.assertNotEqual(response.status_code, 200)
