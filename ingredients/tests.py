from django.test import TestCase
from django.urls import reverse
from ingredients.models import Ingredient
from ingredients.forms import IngredientForm
from recipesingredients.models import RecipeIngredient


class IngredientModelTest(TestCase):
    def setUp(self):
        """Set up test data for Ingredient model."""
        self.ingredient = Ingredient.objects.create(
            name="Sugar",
            introduction="Sweetener",
            pic=None  # Assuming no image is uploaded during testing
        )

    def test_ingredient_creation(self):
        """Test if an Ingredient instance is created correctly."""
        ingredient = Ingredient.objects.create(
            name="Tomato", introduction="Red vegetable")
        self.assertEqual(ingredient.name, "Tomato")
        self.assertEqual(ingredient.introduction, "Red vegetable")

    def test_get_absolute_url(self):
        """Test if get_absolute_url() returns the correct URL."""
        expected_url = reverse(
            'ingredients:ingredient-detail', kwargs={'pk': self.ingredient.pk})
        self.assertEqual(self.ingredient.get_absolute_url(), expected_url)


class IngredientViewsTest(TestCase):
    def setUp(self):
        """Create sample ingredients for testing views."""
        self.ingredient1 = Ingredient.objects.create(
            name="Onion", introduction="Aromatic vegetable")
        self.ingredient2 = Ingredient.objects.create(
            name="Milk", introduction="Dairy product")

    def test_ingredient_list_view(self):
        """Test if IngredientListView loads correctly and displays ingredient names."""
        response = self.client.get(reverse("ingredients:ingredient_list"))
        # Page should load successfully
        self.assertEqual(response.status_code, 200)
        # Check if ingredient name appears
        self.assertContains(response, "Onion")
        self.assertContains(response, "Milk")
        # Ensure correct template is used
        self.assertTemplateUsed(response, "ingredients/list.html")

    def test_ingredient_detail_view(self):
        """Test if IngredientDetailView loads correctly and displays ingredient details."""
        response = self.client.get(
            reverse('ingredients:ingredient-detail', kwargs={'pk': self.ingredient1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ingredient1.name)
        self.assertContains(response, self.ingredient1.introduction)
        self.assertTemplateUsed(response, 'ingredients/detail.html')

    def test_create_ingredient_view(self):
        """Test if IngredientCreateView successfully creates a new ingredient."""
        response = self.client.post(reverse("ingredients:add_ingredient") + "?recipe_id=1", {
            "name": "Egg",
            "introduction": "High protein ingredient",
        }, follow=True)  # Follow the redirect

        # Now expecting 200 after following the redirect
        self.assertEqual(response.status_code, 200)

    def test_create_ingredient_form(self):
        """Test if IngredientForm validates correctly with valid input data."""
        form_data = {
            "name": "Butter",
            "introduction": "Dairy product",
        }
        form = IngredientForm(data=form_data)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_create_ingredient_form_invalid(self):
        """Test if IngredientForm fails validation when the name is missing."""
        form_data = {
            "name": "",  # Empty name should be invalid
            "introduction": "Oil product",
        }
        form = IngredientForm(data=form_data)
        self.assertFalse(form.is_valid())  # Expecting validation to fail
