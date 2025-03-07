from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView   #to display lists and details
from django.shortcuts import redirect
from .models import Ingredient               #to access Ingredient model

from .forms import IngredientForm
from django.urls import reverse_lazy

from recipesingredients.models import RecipeIngredient

# Create your views here.
class IngredientListView(ListView):           #class-based view
   model = Ingredient                         #specify model
   template_name = 'ingredients/list.html'    #specify template 

class IngredientDetailView(DetailView):  # class-based view
    model = Ingredient  # specify model
    template_name = 'ingredients/detail.html'  # specify template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipes"] = RecipeIngredient.objects.filter(
            ingredient=self.object)
        return context
    

class IngredientCreateView(CreateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = "ingredients/ingredient_form.html"

    def form_valid(self, form):
        """store new ingredient and go back to Recipe add ingredient page"""
        self.object = form.save()
        return redirect(reverse_lazy('recipes:recipe_add_ingredients', kwargs={'recipe_id': self.request.GET.get('recipe_id', 1)}))
