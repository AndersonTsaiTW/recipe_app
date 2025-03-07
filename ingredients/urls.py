from django.urls import path
from .views import IngredientListView, IngredientDetailView, IngredientCreateView

app_name = 'ingredients'

urlpatterns = [
    path('list/', IngredientListView.as_view(), name='ingredient_list'),
    path('list/<pk>', IngredientDetailView.as_view(), name='ingredient-detail'),
    path('add/', IngredientCreateView.as_view(), name='add_ingredient'),
]