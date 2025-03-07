"""
URL configuration for recipe_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin

from django.urls import path
from django.urls import include
from django.views.generic import TemplateView
# home page
from recipes.views import home
# for the urls of static pics
from django.conf import settings
from django.conf.urls.static import static

from .views import login_view, logout_success

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('recipes/', include('recipes.urls')),
    path('ingredients/', include('ingredients.urls')),
    path('login/', login_view, name='login'),
    path('logout/', logout_success, name='logout_success'),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about"),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
