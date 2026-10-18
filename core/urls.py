from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/visit-count/', views.visit_count_api, name='visit_count_api'),
    path('links/', views.links, name='links'),
]
