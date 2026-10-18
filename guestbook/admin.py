from django.contrib import admin

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'content', 'created_at')
    search_fields = ('name', 'content')
    readonly_fields = ('created_at',)
