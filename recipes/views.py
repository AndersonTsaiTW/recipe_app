import pandas as pd
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
# to display lists and details
from django.views.generic import ListView, DetailView, CreateView
from .models import Recipe  # to access Recipe model
from .forms import IngredientSearchForm
from .forms import RecipeForm, RecipeIngredientForm, inlineformset_factory
from .utils import generate_chart

from recipesingredients.models import RecipeIngredient
from ingredients.models import Ingredient

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.forms import formset_factory



# Welcome page
def home(request):
    return render(request, 'recipes/recipes_home.html')


# The list of all recipes


class RecipeListView(LoginRequiredMixin, ListView):  # class-based view
    model = Recipe  # specify model
    template_name = 'recipes/list.html'  # specify template

# The detail of recipe


class RecipeDetailView(LoginRequiredMixin, DetailView):  # class-based view
    model = Recipe  # specify model
    template_name = 'recipes/detail.html'  # specify template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ingredients"] = RecipeIngredient.objects.filter(
            recipe=self.object)
        return context


@login_required
def ingredient_search(request):
    """
    Handles ingredient-based recipe search and chart generation.
    Supports three chart types:
    1. Pie Chart (Requires user input of an ingredient)
    2. Bar Chart (Popular ingredients, no user input required)
    3. Line Chart (Recipe growth over time, no user input required)
    """

    chart = None
    error = None
    recipes = Recipe.objects.none()  # make sure `recipes` is a QuerySet
    recipes_df_html = None

    # if GET
    if request.method == "GET":
        form = IngredientSearchForm(request.GET)

        # 1️. Pie Chart (Search by Ingredient)
        if "ingredient" in request.GET and form.is_valid():
            ingredient_name = form.cleaned_data["ingredient"]

            # check ingredient_name
            if not ingredient_name:
                error = "Ingredient name cannot be empty."
            else:
                try:
                    ingredient = Ingredient.objects.get(name=ingredient_name)
                    recipes = Recipe.objects.filter(
                        id__in=RecipeIngredient.objects.filter(
                            ingredient=ingredient
                        ).values_list("recipe", flat=True)
                    )
                except Ingredient.DoesNotExist:
                    recipes = Recipe.objects.none()
                    error = "Ingredient not found."

                # if find fit recipe
                if recipes.exists():
                    df = pd.DataFrame(list(recipes.values(
                        "id", "name", "cooking_time", "ingredient_num", "difficulty")))

                    # make a link
                    df["name"] = df.apply(
                        lambda row: f'<a href="/recipes/list/{row["id"]}">{row["name"]}</a>', axis=1)

                    # rename
                    df.rename(columns={
                        "name": "Recipe Name",
                        "cooking_time": "Cooking Time (min)",
                        "ingredient_num": "Ingredient Count",
                        "difficulty": "Difficulty"
                    }, inplace=True)

                    # transfer DataFrame to HTML
                    recipes_df_html = df.to_html(
                        index=False, classes="table table-striped", escape=False)

                # creat Pie Chart
                if not error:
                    chart, error = generate_chart("#1", ingredient_name)

        # 2️. Bar Chart (No input required)
        elif request.GET.get("chart") == "#2":
            chart, error = generate_chart("#2")

        # 3️. Line Chart (No input required)
        elif request.GET.get("chart") == "#3":
            chart, error = generate_chart("#3")

    else:
        form = IngredientSearchForm()

    return render(request, "recipes/ingredient_search.html", {
        "form": form,
        "recipes": recipes,
        "chart": chart,
        "error": error,
        "recipes_df": recipes_df_html
    })


class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/recipe_form.html"
    success_url = reverse_lazy('recipes:recipe_list')

    def form_valid(self, form):
        """儲存 Recipe 並轉跳到新增 RecipeIngredient 的頁面"""
        form.instance.created_by = self.request.user
        self.object = form.save()  # store Recipe

        # direct to RecipeIngredient
        return redirect('recipes:recipe_add_ingredients', recipe_id=self.object.pk)

class RecipeIngredientCreateView(LoginRequiredMixin, CreateView):
    template_name = "recipes/recipe_ingredient_form.html"
    
    def get(self, request, recipe_id):
        """show RecipeIngredient"""
        recipe = Recipe.objects.get(pk=recipe_id)
        ingredient_num = recipe.ingredient_num  # get ingredient num
        IngredientFormSet = formset_factory(RecipeIngredientForm, extra=ingredient_num)  # generate
        formset = IngredientFormSet()
        return render(request, self.template_name, {"formset": formset, "recipe": recipe})

    def post(self, request, recipe_id):
        """store RecipeIngredient"""
        recipe = Recipe.objects.get(pk=recipe_id)
        IngredientFormSet = formset_factory(RecipeIngredientForm)
        formset = IngredientFormSet(request.POST)

        if formset.is_valid():
            for form in formset:
                ingredient_name = form.cleaned_data.get('ingredient', '')
                quantity = form.cleaned_data.get('quantity', '')

                if not ingredient_name or not quantity:
                    continue

    
                ingredient, created = Ingredient.objects.get_or_create(name=ingredient_name)

                recipe_ingredient = form.save(commit=False)
                recipe_ingredient.ingredient = ingredient  #  `Ingredient` Model instance
                recipe_ingredient.recipe = recipe
                recipe_ingredient.save()

            return redirect('recipes:recipe_list')  # store and go to Recipe list
        
        return render(request, self.template_name, {"formset": formset, "recipe": recipe})

