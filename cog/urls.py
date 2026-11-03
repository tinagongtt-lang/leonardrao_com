from django.urls import path

from . import views

app_name = 'cog'

urlpatterns = [
    path('', views.home, name='home'),
]
