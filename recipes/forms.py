from django import forms
from .models import Recipe
from recipesingredients.models import RecipeIngredient
from ingredients.models import Ingredient
from django.urls import reverse_lazy

from django.forms import inlineformset_factory

class IngredientSearchForm(forms.Form):
    ingredient = forms.CharField(
        label="Ingredient Name",
        max_length=100,
        required=False
    )
class RecipeForm(forms.ModelForm):
    ingredient_num = forms.IntegerField(
        min_value=1,
        label="Number of Ingredients",
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'ingredient-num'})
    )

    class Meta:
        model = Recipe
        fields = ['name', 'cooking_time', 'pic', 'ingredient_num']


class RecipeIngredientForm(forms.ModelForm):
    ingredient = forms.ModelChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    quantity = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2 cups'}),
        required=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredient'].widget.attrs['onchange'] = 'checkNewIngredient()'

RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    extra=0, 
    can_delete=True
)
