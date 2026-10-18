from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_home, name='home'),
    path('friend/add/', views.add_friend, name='add_friend'),
    path('friend-request/<int:pk>/<str:action>/', views.friend_request_respond, name='friend_request_respond'),
    path('invite/<int:pk>/<str:action>/', views.room_invite_respond, name='room_invite_respond'),
    path('room/new/', views.room_create, name='room_create'),
    path('room/<str:code>/', views.room_detail, name='room'),
    path('room/<str:code>/add/', views.room_add_member, name='room_add_member'),
    path('room/<str:code>/add-friend/', views.room_add_friend, name='room_add_friend'),
    path('room/<str:code>/leave/', views.room_leave, name='room_leave'),
    path('room/<str:code>/upload/', views.room_upload, name='room_upload'),
    path('link-preview/', views.link_preview, name='link_preview'),
    path('room/<str:code>/kick/', views.room_kick, name='room_kick'),
    path('room/<str:code>/disband/', views.room_disband, name='room_disband'),
    path('room/<str:code>/admin/<str:action>/', views.room_admin, name='room_admin'),
    path('invite/<int:pk>/approve/<str:action>/', views.invite_approve, name='invite_approve'),
]
