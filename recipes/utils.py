import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.db.models import Count
from django.db.models.functions import TruncDate

from recipes.models import Recipe
from recipesingredients.models import RecipeIngredient
from ingredients.models import Ingredient


def get_graph(fig):
    """Convert Matplotlib figure to base64-encoded image"""
    buffer = BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    return img_base64


def generate_chart(chart_type, ingredient_name=None):
    """
    Generate a chart based on the provided chart type.

    Parameters:
    - chart_type (str): The type of chart to generate ('#1' for Pie, '#2' for Bar, '#3' for Line).
    - ingredient_name (str, optional): The ingredient to filter recipes by (only used for Pie chart).

    Returns:
    - str: Base64-encoded image string.
    - str: Error message (if any).
    """

    # **1️. Pie Chart: Recipe Difficulty Distribution (Requires Ingredient Input)**
    if chart_type == "#1":
        if not ingredient_name:
            return None, "Ingredient name is required for Pie Chart."

        try:
            ingredient = Ingredient.objects.get(name=ingredient_name)
        except Ingredient.DoesNotExist:
            return None, "Ingredient not found."

        # Get recipes containing this ingredient
        recipes_with_ingredient = RecipeIngredient.objects.filter(
            ingredient=ingredient).values_list("recipe", flat=True)

        # Count difficulty levels
        difficulty_counts = Recipe.objects.filter(id__in=recipes_with_ingredient).values(
            "difficulty").annotate(count=Count("id"))

        # Convert to dictionary
        difficulty_data = {entry["difficulty"]: entry["count"]
                           for entry in difficulty_counts}

        # Ensure all difficulty levels are represented
        difficulty_labels = ["Easy", "Medium", "Intermediate", "Hard"]
        difficulty_values = [difficulty_data.get(
            level, 0) for level in difficulty_labels]

        # **Generate pie chart using fig, ax**
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(difficulty_values, labels=difficulty_labels, autopct="%1.1f%%",
               colors=["green", "orange", "blue", "red"])
        ax.set_title(f"Recipes with {ingredient_name} by Difficulty")

    # **2️. Bar Chart: Most Popular Ingredients (No User Input Needed)**
    elif chart_type == "#2":
        # Count how many recipes contain each ingredient
        ingredient_counts = RecipeIngredient.objects.values("ingredient__name").annotate(
            # Top 10 ingredients
            count=Count("recipe")).order_by("-count")[:10]

        if not ingredient_counts.exists():
            return None, "No ingredient data available."

        # Extract data
        ingredient_names = [entry["ingredient__name"]
                            for entry in ingredient_counts]
        recipe_counts = [entry["count"] for entry in ingredient_counts]

        # Generate bar chart
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(ingredient_names, recipe_counts, color="blue")
        ax.set_xlabel("Number of Recipes")
        ax.set_ylabel("Ingredients")
        ax.set_title("Top 10 Most Popular Ingredients in Recipes")
        ax.invert_yaxis()  # Invert Y-axis for better readability (most popular at the top)

    # **3️. Line Chart: Recipe Growth Over Time (No User Input Needed)**
    elif chart_type == "#3":
        # Aggregate recipes by day
        daily_recipe_counts = Recipe.objects.annotate(
            day=TruncDate("created_at")
        ).values("day").annotate(count=Count("id")).order_by("day")

        if not daily_recipe_counts.exists():
            return None, "No data available for recipe growth."

        # Extract data
        days = [entry["day"].strftime("%Y-%m-%d")
                for entry in daily_recipe_counts]
        recipe_counts = [entry["count"] for entry in daily_recipe_counts]

        # Generate line chart
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.plot(days, recipe_counts, marker="o", linestyle="-", color="blue")
        ax.set_xlabel("Day")
        ax.set_ylabel("Number of Recipes Added")
        ax.set_ylim(0, max(recipe_counts) + 1)  # Adding 1 for padding

        if len(days) > 1:
            ax.set_xticks(range(len(days)))
            ax.set_xticklabels(days, rotation=45)

        ax.set_title("Recipe Growth Over Time (Daily)")

    else:
        return None, "Invalid chart type."

    # Convert graph to base64
    img_base64 = get_graph(fig)
    return f"data:image/png;base64,{img_base64}", None
