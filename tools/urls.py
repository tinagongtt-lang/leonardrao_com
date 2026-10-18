from django.urls import path

from . import views

app_name = 'tools'

urlpatterns = [
    path('', views.index, name='index'),
    path('timer/', views.timer, name='timer'),
    path('stopwatch/', views.stopwatch, name='stopwatch'),
    path('base-converter/', views.base_converter, name='base_converter'),
]
