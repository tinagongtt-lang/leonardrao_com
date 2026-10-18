from django.contrib import admin

from .models import AboutMe, BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'content')


@admin.register(AboutMe)
class AboutMeAdmin(admin.ModelAdmin):
    pass
