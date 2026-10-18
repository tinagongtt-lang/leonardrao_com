from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

app_name = 'blog'

urlpatterns = [
    path('', views.blog_home, name='blog_home'),
    path('write/', views.post_create, name='post_create'),
    path('about/', views.about_me, name='about_me'),
    path('about/edit/', views.about_me_edit, name='about_me_edit'),
    path('upload/', views.upload_media, name='upload_media'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html', form_class=LoginForm), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='core:home'), name='logout'),
    path('<str:username>/', views.author_detail, name='author_detail'),
    path('<str:username>/<int:pk>/', views.post_detail, name='post_detail'),
    path('<str:username>/<int:pk>/comment/', views.comment_create, name='comment_create'),
    path('<str:username>/<int:pk>/comment/<int:comment_pk>/delete/', views.comment_delete, name='comment_delete'),
    path('<str:username>/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('<str:username>/<int:pk>/delete/', views.post_delete, name='post_delete'),
]
