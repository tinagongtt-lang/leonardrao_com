from django.urls import path

from . import views

app_name = 'games'

urlpatterns = [
    path('', views.index, name='index'),
    path('2048/', views.game2048, name='2048'),
    path('maze3d/', views.maze3d, name='maze3d'),
    path('chess/', views.chess_home, name='chess'),
    path('chess/new/', views.chess_new, name='chess_new'),
    path('chess/<str:code>/', views.chess_detail, name='chess_detail'),
    path('xiangqi/', views.xiangqi_home, name='xiangqi'),
    path('xiangqi/new/', views.xiangqi_new, name='xiangqi_new'),
    path('xiangqi/<str:code>/', views.xiangqi_detail, name='xiangqi_detail'),
    path('go/', views.go_home, name='go'),
    path('go/new/', views.go_new, name='go_new'),
    path('go/<str:code>/', views.go_detail, name='go_detail'),
    path('gomoku/', views.gomoku_home, name='gomoku'),
    path('gomoku/new/', views.gomoku_new, name='gomoku_new'),
    path('gomoku/<str:code>/', views.gomoku_detail, name='gomoku_detail'),
]
