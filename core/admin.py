from django.contrib import admin

from .models import FriendlyLink, VisitCounter


@admin.register(VisitCounter)
class VisitCounterAdmin(admin.ModelAdmin):
    list_display = ('name', 'count')
    readonly_fields = ('name',)


@admin.register(FriendlyLink)
class FriendlyLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'created_at')
